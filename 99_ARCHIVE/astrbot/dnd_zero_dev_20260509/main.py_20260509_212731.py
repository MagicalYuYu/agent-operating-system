"""
DND/Zero TRPG 插件主文件
基于 D&D 5e 规则的轻量化群组跑团插件

数据来源: 5etools中文站 (https://5e.kiwee.top/)
遵循 Creative Commons 许可证
"""
import json
import random
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star
from astrbot.api import logger, AstrBotConfig
from astrbot.api.event import filter as event_filter

import astrbot.api.message_components as Comp
from astrbot.api.event import MessageChain

from .util import DataManager, check_permission, get_group_data_path
from .data.loader import DataLoader
from .core import (
    DiceRoller, Character, AbilityScores, Skills, CharacterFactory,
    SkillChecker, CombatSystem, SpellDatabase, AdvantageType
)
from pathlib import Path
from astrbot.core.utils.astrbot_path import get_astrbot_data_path


class DNDZeroPlugin(Star):
    """DND/Zero TRPG 插件主类"""

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.context = context
        self.config = config
        plugin_data_path = Path(get_astrbot_data_path()) / "plugin_data" / "astrbot_plugin_dnd_zero"
        plugin_data_path.mkdir(parents=True, exist_ok=True)
        self.plugin_data_dir = plugin_data_path
        self.backup_dir = self.plugin_data_dir / "backup"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.data_manager = DataManager(self.plugin_data_dir)
        self.data_loader = DataLoader(self.plugin_data_dir)
        self.skill_checker = SkillChecker()
        self.combat_system = CombatSystem()
        self.characters: Dict[str, Character] = {}
        logger.info("DND/Zero 插件初始化完成")

    async def initialize(self):
        """插件初始化钩子"""
        logger.info("DND/Zero 插件开始初始化...")
        await self._load_plugin_data()
        await self._preload_data()
        logger.info("DND/Zero 插件数据加载完成")

    async def _preload_data(self):
        """预加载常用数据"""
        try:
            await self.data_loader.get_classes()
            await self.data_loader.get_races()
            logger.info("D&D 数据预加载完成")
        except Exception as e:
            logger.warning(f"数据预加载失败: {e}")

    async def _load_plugin_data(self):
        """加载插件数据"""
        characters_data = self.data_manager.load_json("characters.json")
        if characters_data:
            for user_id, char_data in characters_data.items():
                try:
                    abilities = AbilityScores(**char_data.get('abilities', {}))
                    char = Character(
                        name=char_data.get('name', '未命名'),
                        player_id=user_id,
                        level=char_data.get('level', 1),
                        experience=char_data.get('experience', 0),
                        abilities=abilities,
                        class_name=char_data.get('class_name', ''),
                        subclass=char_data.get('subclass', ''),
                        race=char_data.get('race', ''),
                        hit_points=char_data.get('hit_points', 10),
                        max_hit_points=char_data.get('max_hit_points', 10),
                        armor_class=char_data.get('armor_class', 10)
                    )
                    self.characters[user_id] = char
                except Exception as e:
                    logger.error(f"加载角色数据失败 {user_id}: {e}")

    def _save_plugin_data(self):
        """保存插件数据"""
        characters_data = {}
        for user_id, char in self.characters.items():
            characters_data[user_id] = {
                'name': char.name,
                'level': char.level,
                'experience': char.experience,
                'abilities': {
                    'strength': char.abilities.strength,
                    'dexterity': char.abilities.dexterity,
                    'constitution': char.abilities.constitution,
                    'intelligence': char.abilities.intelligence,
                    'wisdom': char.abilities.wisdom,
                    'charisma': char.abilities.charisma
                },
                'class_name': char.class_name,
                'subclass': char.subclass,
                'race': char.race,
                'hit_points': char.hit_points,
                'max_hit_points': char.max_hit_points,
                'armor_class': char.armor_class
            }
        self.data_manager.save_json("characters.json", characters_data)

    def _backup_file(self, filepath: Path):
        """备份文件到 backup 目录"""
        if filepath.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{filepath.stem}_{timestamp}{filepath.suffix}"
            backup_path = self.backup_dir / backup_name
            import shutil
            try:
                shutil.copy2(filepath, backup_path)
                logger.info(f"文件已备份: {backup_path}")
            except Exception as e:
                logger.error(f"备份文件失败: {e}")

    def _check_group_permission(self, event: AstrMessageEvent) -> bool:
        """检查群组权限"""
        group_id = event.get_group_id()
        if not group_id:
            return False

        whitelist_mode = self.config.get("whitelist_mode", False)
        if whitelist_mode:
            whitelist_groups = self.config.get("whitelist_groups", [])
            if str(group_id) not in [str(g) for g in whitelist_groups]:
                return False

        return True

    def _check_superadmin(self, event: AstrMessageEvent) -> bool:
        """检查超级管理员权限"""
        user_id = event.get_sender_id()
        superadmins = self.config.get("superadmins", [])
        return check_permission(user_id, superadmins)

    def _get_help_menu(self) -> str:
        """获取帮助菜单文本"""
        help_text = """
✨ **DND/Zero 群组跑团插件 v0.1.0** ✨

📜 **基础指令：**
  /dnd menu      - 显示本菜单
  /dnd help      - 获取帮助信息

🎲 **骰子系统：**
  /dnd roll <骰子>     - 掷骰（如 /dnd roll d20, /dnd roll 2d6+3）
  /dnd init           - 先攻掷骰

👤 **角色系统：**
  /dnd create         - 创建角色（交互式）
  /dnd status         - 查看我的角色状态
  /dnd abilities      - 查看属性面板

🎯 **检定系统：**
  /dnd skill <技能>   - 技能检定
  /dnd save <属性>    - 豁免检定

⚔️ **战斗系统：**
  /dnd attack <目标>  - 攻击检定
  /dnd dmg <伤害骰>   - 伤害掷骰

📖 **法术系统：**
  /dnd spell <法术名> - 查询法术信息
  /dnd spells         - 查看已知法术

🎭 **娱乐系统：**
  /dnd quote          - 随机DND名言

🔧 **管理员指令：**
  /dnd admin reload    - 重载插件配置
  /dnd admin status    - 查看插件状态

💡 **使用说明：**
  1. 首先使用 /dnd create 创建你的角色
  2. 使用 /dnd status 查看角色信息
  3. 使用 /dnd roll 开始掷骰冒险

数据来源: 5etools中文站 | 遵循 Creative Commons 许可证
如需更多帮助，请联系插件管理员。
        """.strip()
        return help_text

    @filter.command_group("dnd")
    def dnd(self):
        """DND 指令组"""
        pass

    @dnd.command("menu")
    @filter.event_message_type(event_filter.EventMessageType.GROUP_MESSAGE)
    async def dnd_menu(self, event: AstrMessageEvent):
        """显示 DND 菜单"""
        if not self._check_group_permission(event):
            yield event.plain_result("⚠️ 此群组未被授权使用 DND 插件")
            event.stop_event()
            return

        help_text = self._get_help_menu()
        user_id = event.get_sender_id()
        chain = [
            Comp.At(qq=user_id),
            Comp.Plain("\n\n" + help_text)
        ]
        yield event.chain_result(chain)

    @dnd.command("help")
    @filter.event_message_type(event_filter.EventMessageType.GROUP_MESSAGE)
    async def dnd_help(self, event: AstrMessageEvent):
        """获取帮助信息"""
        if not self._check_group_permission(event):
            yield event.plain_result("⚠️ 此群组未被授权使用 DND 插件")
            event.stop_event()
            return

        help_text = self._get_help_menu()
        user_id = event.get_sender_id()
        chain = [
            Comp.At(qq=user_id),
            Comp.Plain("\n\n" + help_text)
        ]
        yield event.chain_result(chain)

    @dnd.command("roll")
    @filter.event_message_type(event_filter.EventMessageType.GROUP_MESSAGE)
    async def dnd_roll(self, event: AstrMessageEvent, dice: str = "d20"):
        """掷骰"""
        if not self._check_group_permission(event):
            yield event.plain_result("⚠️ 此群组未被授权使用 DND 插件")
            event.stop_event()
            return

        try:
            result = DiceRoller.roll_from_notation(dice)
            user_id = event.get_sender_id()

            result_text = f"🎲 **{event.get_sender_name()}** 掷 **{dice}**\n"
            result_text += f"━━━━━━━━━━━━━━━━━━━━\n"
            result_text += f"结果: **{result.total}**\n"
            result_text += f"详情: {str(result)}"

            if result.dice_type == 20 and result.dice_count == 1:
                if 20 in result.rolls:
                    result_text += "\n✨ **大成功！**"
                elif 1 in result.rolls:
                    result_text += "\n💀 **大失败！**"

            yield event.plain_result(result_text)

        except ValueError as e:
            yield event.plain_result(f"❌ 无效的骰子格式！\n请使用格式如: d20, 2d6, 1d8+3")

    @dnd.command("init")
    @filter.event_message_type(event_filter.EventMessageType.GROUP_MESSAGE)
    async def dnd_initiative(self, event: AstrMessageEvent):
        """先攻掷骰"""
        if not self._check_group_permission(event):
            yield event.plain_result("⚠️ 此群组未被授权使用 DND 插件")
            event.stop_event()
            return

        user_id = str(event.get_sender_id())
        if user_id in self.characters:
            char = self.characters[user_id]
            dex_mod = char.abilities.get_modifier("dexterity")
            result = DiceRoller.roll_initiative(dex_mod)
        else:
            result = DiceRoller.roll_d20()

        result_text = f"🎯 **先攻检定** - {event.get_sender_name()}\n"
        result_text += f"━━━━━━━━━━━━━━━━━━━━\n"
        result_text += f"D20: **{result.roll}**"
        if user_id in self.characters:
            result_text += f" + {dex_mod:+d}（敏捷）"
        result_text += f"\n━━━━━━━━━━━━━━━━━━━━\n"
        result_text += f"先攻值: **{result.total}**"

        yield event.plain_result(result_text)

    @dnd.command("create")
    @filter.event_message_type(event_filter.EventMessageType.GROUP_MESSAGE)
    async def dnd_create(self, event: AstrMessageEvent):
        """创建角色"""
        if not self._check_group_permission(event):
            yield event.plain_result("⚠️ 此群组未被授权使用 DND 插件")
            event.stop_event()
            return

        user_id = str(event.get_sender_id())
        if user_id in self.characters:
            yield event.plain_result(f"⚠️ 你已经创建过角色了！\n使用 /dnd status 查看角色信息。")
            return

        user_name = event.get_sender_name()
        abilities = AbilityScores(
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8
        )

        char = Character(
            name=user_name,
            player_id=user_id,
            level=1,
            abilities=abilities,
            class_name="战士",
            race="人类",
            hit_points=10 + abilities.get_modifier("constitution"),
            max_hit_points=10 + abilities.get_modifier("constitution"),
            armor_class=10 + abilities.get_modifier("dexterity")
        )

        self.characters[user_id] = char
        self._save_plugin_data()

        yield event.plain_result(f"✅ 角色创建成功！\n\n{char.to_summary()}")

    @dnd.command("status")
    @filter.event_message_type(event_filter.EventMessageType.GROUP_MESSAGE)
    async def dnd_status(self, event: AstrMessageEvent):
        """查看角色状态"""
        if not self._check_group_permission(event):
            yield event.plain_result("⚠️ 此群组未被授权使用 DND 插件")
            event.stop_event()
            return

        user_id = str(event.get_sender_id())
        if user_id not in self.characters:
            yield event.plain_result(f"⚠️ 你还没有创建角色！\n使用 /dnd create 创建角色。")
            return

        char = self.characters[user_id]
        yield event.plain_result(char.to_summary())

    @dnd.command("abilities")
    @filter.event_message_type(event_filter.EventMessageType.GROUP_MESSAGE)
    async def dnd_abilities(self, event: AstrMessageEvent):
        """查看属性面板"""
        if not self._check_group_permission(event):
            yield event.plain_result("⚠️ 此群组未被授权使用 DND 插件")
            event.stop_event()
            return

        user_id = str(event.get_sender_id())
        if user_id not in self.characters:
            yield event.plain_result(f"⚠️ 你还没有创建角色！\n使用 /dnd create 创建角色。")
            return

        char = self.characters[user_id]
        mods = char.abilities.get_all_modifiers()

        abilities_text = f"📊 **属性面板** - {char.name}\n"
        abilities_text += f"━━━━━━━━━━━━━━━━━━━━\n"
        abilities_text += f"力量:     {char.abilities.strength:>2} ({self._format_mod(mods['strength'])})\n"
        abilities_text += f"敏捷:     {char.abilities.dexterity:>2} ({self._format_mod(mods['dexterity'])})\n"
        abilities_text += f"体质:     {char.abilities.constitution:>2} ({self._format_mod(mods['constitution'])})\n"
        abilities_text += f"智力:     {char.abilities.intelligence:>2} ({self._format_mod(mods['intelligence'])})\n"
        abilities_text += f"感知:     {char.abilities.wisdom:>2} ({self._format_mod(mods['wisdom'])})\n"
        abilities_text += f"魅力:     {char.abilities.charisma:>2} ({self._format_mod(mods['charisma'])})\n"
        abilities_text += f"━━━━━━━━━━━━━━━━━━━━\n"
        abilities_text += f"HP: {char.hit_points}/{char.max_hit_points} | AC: {char.armor_class} | 熟练: +{char.proficiency_bonus}"

        yield event.plain_result(abilities_text)

    @dnd.command("skill")
    @filter.event_message_type(event_filter.EventMessageType.GROUP_MESSAGE)
    async def dnd_skill(self, event: AstrMessageEvent, *, skill: str = ""):
        """技能检定"""
        if not self._check_group_permission(event):
            yield event.plain_result("⚠️ 此群组未被授权使用 DND 插件")
            event.stop_event()
            return

        if not skill:
            skills_list = self.skill_checker.get_all_skills()
            yield event.plain_result(f"🎯 **技能列表**\n\n可用技能:\n" + "\n".join(f"• {s}" for s in skills_list))
            return

        user_id = str(event.get_sender_id())
        if user_id in self.characters:
            char = self.characters[user_id]
            result = self.skill_checker.roll_skill_check(char, skill, dc=10)
        else:
            result = self.skill_checker.roll_skill_check(
                Character(name="无名冒险者", player_id="test", abilities=AbilityScores()),
                skill, dc=10
            )

        result_text = f"🎯 **技能检定** - {skill}\n"
        result_text += f"━━━━━━━━━━━━━━━━━━━━\n"
        result_text += f"检定者: {event.get_sender_name()}\n"
        result_text += f"D20: **{result.roll}**\n"
        result_text += f"属性调整: {self._format_mod(result.ability_modifier)}"
        if result.proficiency_bonus > 0:
            result_text += f"\n熟练加值: +{result.proficiency_bonus}"
        result_text += f"\n━━━━━━━━━━━━━━━━━━━━\n"
        result_text += f"总计: **{result.total}** vs DC 10\n"
        result_text += f"✨ **成功！**" if result.success else f"❌ **失败！**"

        if result.is_critical:
            result_text += "\n🌟 **大成功！**"
        elif result.is_fumble:
            result_text += "\n💀 **大失败！**"

        yield event.plain_result(result_text)

    @dnd.command("save")
    @filter.event_message_type(event_filter.EventMessageType.GROUP_MESSAGE)
    async def dnd_save(self, event: AstrMessageEvent, *, ability: str = ""):
        """豁免检定"""
        if not self._check_group_permission(event):
            yield event.plain_result("⚠️ 此群组未被授权使用 DND 插件")
            event.stop_event()
            return

        if not ability:
            yield event.plain_result(f"🎯 **豁免检定**\n\n用法: /dnd save <属性>\n可选: str(力量), dex(敏捷), con(体质), int(智力), wis(感知), cha(魅力)")
            return

        ability_map = {
            "str": "strength", "力量": "strength",
            "dex": "dexterity", "敏捷": "dexterity",
            "con": "constitution", "体质": "constitution",
            "int": "intelligence", "智力": "intelligence",
            "wis": "wisdom", "感知": "wisdom",
            "cha": "charisma", "魅力": "charisma"
        }

        ability_key = ability_map.get(ability.lower(), ability.lower())

        user_id = str(event.get_sender_id())
        if user_id in self.characters:
            char = self.characters[user_id]
            mod = char.abilities.get_modifier(ability_key)
            result = DiceRoller.roll_d20()
            total = result.roll + mod
        else:
            result = DiceRoller.roll_d20()
            total = result.roll

        result_text = f"🛡️ **豁免检定** - {ability}\n"
        result_text += f"━━━━━━━━━━━━━━━━━━━━\n"
        result_text += f"检定者: {event.get_sender_name()}\n"
        result_text += f"D20: **{result.roll}**"
        if user_id in self.characters:
            result_text += f" + {self._format_mod(mod)}"
        result_text += f"\n━━━━━━━━━━━━━━━━━━━━\n"
        result_text += f"总计: **{total}**"

        yield event.plain_result(result_text)

    @dnd.command("attack")
    @filter.event_message_type(event_filter.EventMessageType.GROUP_MESSAGE)
    async def dnd_attack(self, event: AstrMessageEvent, *, target: str = "敌人"):
        """攻击检定"""
        if not self._check_group_permission(event):
            yield event.plain_result("⚠️ 此群组未被授权使用 DND 插件")
            event.stop_event()
            return

        user_id = str(event.get_sender_id())
        if user_id in self.characters:
            char = self.characters[user_id]
            attack_bonus = char.get_attack_bonus()
            result = DiceRoller.roll_attack(attack_bonus)
        else:
            attack_bonus = 0
            result = DiceRoller.roll_d20()
            result.total = result.roll

        target_ac = 15

        result_text = f"⚔️ **攻击检定** vs {target} (AC {target_ac})\n"
        result_text += f"━━━━━━━━━━━━━━━━━━━━\n"
        result_text += f"攻击者: {event.get_sender_name()}\n"
        result_text += f"D20: **{result.roll}** + {attack_bonus} = **{result.total}**\n"
        result_text += f"━━━━━━━━━━━━━━━━━━━━\n"

        if result.is_critical:
            result_text += "🎯 **暴击！自动命中！**"
        elif result.is_fumble:
            result_text += "💀 **大失败！**"
        elif result.total >= target_ac:
            result_text += "✅ **命中！**"
        else:
            result_text += "❌ **未命中！**"

        yield event.plain_result(result_text)

    @dnd.command("dmg")
    @filter.event_message_type(event_filter.EventMessageType.GROUP_MESSAGE)
    async def dnd_damage(self, event: AstrMessageEvent, *, dice: str = "1d6"):
        """伤害掷骰"""
        if not self._check_group_permission(event):
            yield event.plain_result("⚠️ 此群组未被授权使用 DND 插件")
            event.stop_event()
            return

        try:
            result = DiceRoller.roll_from_notation(dice)

            result_text = f"💥 **伤害掷骰**\n"
            result_text += f"━━━━━━━━━━━━━━━━━━━━\n"
            result_text += f"伤害骰: **{dice}**\n"
            result_text += f"结果: **{result.total}**\n"
            result_text += f"详情: {str(result)}"

            yield event.plain_result(result_text)

        except ValueError:
            yield event.plain_result(f"❌ 无效的骰子格式！\n请使用格式如: 1d6, 2d8+3")

    @dnd.command("spells")
    @filter.event_message_type(event_filter.EventMessageType.GROUP_MESSAGE)
    async def dnd_spells(self, event: AstrMessageEvent):
        """查看已知法术"""
        if not self._check_group_permission(event):
            yield event.plain_result("⚠️ 此群组未被授权使用 DND 插件")
            event.stop_event()
            return

        spells = SpellDatabase.get_all_spells()
        spells_by_level = {}
        for spell in spells:
            level = spell.get_level_string()
            if level not in spells_by_level:
                spells_by_level[level] = []
            spells_by_level[level].append(spell.name)

        result_text = f"📖 **法术列表** (共 {len(spells)} 个)\n"
        result_text += f"━━━━━━━━━━━━━━━━━━━━\n"
        for level, spell_list in spells_by_level.items():
            result_text += f"\n**{level}**: {', '.join(spell_list)}"

        result_text += f"\n\n使用 /dnd spell <法术名> 查看详情"

        yield event.plain_result(result_text)

    @dnd.command("spell")
    @filter.event_message_type(event_filter.EventMessageType.GROUP_MESSAGE)
    async def dnd_spell(self, event: AstrMessageEvent, *, spell_name: str = ""):
        """查询法术信息"""
        if not self._check_group_permission(event):
            yield event.plain_result("⚠️ 此群组未被授权使用 DND 插件")
            event.stop_event()
            return

        if not spell_name:
            yield event.plain_result("请提供法术名称，如: /dnd spell fireball")
            return

        spell = SpellDatabase.get_spell(spell_name)
        if not spell:
            results = SpellDatabase.search_spells(spell_name)
            if results:
                result_text = f"🔍 搜索 '{spell_name}' 的结果:\n"
                result_text += "\n".join(f"• {s.name} ({s.get_level_string()})" for s in results[:5])
                result_text += f"\n\n使用 /dnd spell <法术名> 查看详情"
            else:
                result_text = f"❌ 未找到法术 '{spell_name}'"
            yield event.plain_result(result_text)
            return

        result_text = f"📖 **{spell.name}**\n"
        result_text += f"━━━━━━━━━━━━━━━━━━━━\n"
        result_text += f"环阶: {spell.get_level_string()} | 学派: {spell.school}\n"
        result_text += f"施法时间: {spell.casting_time}\n"
        result_text += f"距离: {spell.range}\n"
        result_text += f"持续时间: {spell.duration}\n"
        result_text += f"━━━━━━━━━━━━━━━━━━━━\n"
        result_text += f"{spell.description}\n"
        if spell.higher_level_effect:
            result_text += f"\n**高环效果**: {spell.higher_level_effect}\n"
        result_text += f"\n可使用职业: {', '.join(spell.classes)}"

        yield event.plain_result(result_text)

    @dnd.command("quote")
    @filter.event_message_type(event_filter.EventMessageType.GROUP_MESSAGE)
    async def dnd_quote(self, event: AstrMessageEvent):
        """随机DND名言"""
        quotes = [
            "「在这个世界上，只有死亡是确定无疑的。」 - 《死亡公主》",
            "「不要相信任何人，尤其是那些看起来友善的人。」 - 某位老练的冒险者",
            "「真正的魔法，来自于勇气和信念。」 - 大法师艾拉隆",
            "「每一次冒险，都是命运的骰子。」 - 传奇游侠卡拉斯",
            "「在黑暗中，只有火光照亮前路。」 - 炉火守护者",
            "「金币可以买到很多东西，但买不到第二次机会。」 - 矮人矿工长格罗姆",
            "「真正的宝藏，是旅途中的伙伴。」 - 吟游诗人奥萝拉",
            "「死亡不是终点，而是新的开始。」 - 牧师大祭司",
            "「勇气不是没有恐惧，而是即使恐惧也要前行。」 - 圣武士雷鸣",
            "「相信你的骰子，也要相信你的队友。」 - 龙裔战士卡奥斯"
        ]
        yield event.plain_result(random.choice(quotes))

    @dnd.command("admin")
    @filter.event_message_type(event_filter.EventMessageType.GROUP_MESSAGE)
    async def dnd_admin(self, event: AstrMessageEvent, action: str = ""):
        """管理员指令"""
        if not self._check_superadmin(event):
            yield event.plain_result("⚠️ 此指令仅限超级管理员使用")
            event.stop_event()
            return

        if action == "reload":
            await self._load_plugin_data()
            yield event.plain_result("✅ 插件配置已重载")
        elif action == "status":
            status_info = f"""
📊 **DND/Zero 插件状态**

插件版本: v0.1.0 Demo
数据目录: {self.plugin_data_dir}
注册角色: {len(self.characters)} 个
超级管理员: {len(self.config.get('superadmins', []))} 人
白名单模式: {'已启用' if self.config.get('whitelist_mode', False) else '已禁用'}

数据来源: 5etools中文站
            """.strip()
            yield event.plain_result(status_info)
        else:
            yield event.plain_result("⚠️ 无效的管理员指令。\n可用: /dnd admin reload, /dnd admin status")

    async def on_astrbot_loaded(self):
        """AstrBot 初始化完成的钩子"""
        logger.info("AstrBot 已加载，DND/Zero 插件准备就绪")

    async def on_llm_request(self, event: AstrMessageEvent, req):
        """LLM 请求钩子"""
        pass

    async def on_llm_response(self, event: AstrMessageEvent, resp):
        """LLM 响应钩子"""
        pass

    @staticmethod
    def _format_mod(modifier: int) -> str:
        """格式化调整值"""
        return f"+{modifier}" if modifier >= 0 else str(modifier)
