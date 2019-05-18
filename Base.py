from Objects import *


class Game:
    def __init__(self):
        self.go_back = False
        self.test_mode = True
        self.crit_modifier = 1.5
        self.dice_range = 20

    def pre_start(self):
        for char in characters:
            char.set_abilities()
            char.set_damage(weapons)
        self.roll_initiative()
        self.sort_initiative()
        self.print_initiative()
        return characters

    @staticmethod
    def get_stats():
        for char in players:
            char.get_stats()
        for char in players_corpses:
            char.get_stats()
        for char in enemies:
            char.get_stats()
        for char in enemies_corpses:
            char.get_stats()

    @staticmethod
    def past_turn(char):
        for now in char.abilities:
            char.dur_reduce(now['ability'])
            char.cd_reduce(now['ability'])

    @staticmethod
    def death_check():
        for char in characters:
            if char.hp == 0:
                for effect in char.buffs:
                    char.set_effects_to_0(effect)
                for effect in char.debuffs:
                    char.set_effects_to_0(effect)
                for effect in char.auras:
                    char.set_effects_to_0(effect)
                for now in char.abilities:
                    now['duration'] = -1
                    now['cooldown'] = -1
                if char.side == 'players':
                    players.remove(char)
                    players_corpses.append(char)
                elif char.side == 'enemies':
                    enemies.remove(char)
                    enemies_corpses.append(char)
                characters.remove(char)
        return characters

    @staticmethod
    def roll_initiative():
        initiative = random.sample(range(100), len(characters))
        i = 0
        for ink in initiative:
            characters[i].initiative = ink
            i += 1

        for character in characters:
            if character.side == 'players':
                players.append(character)
            elif character.side == 'enemies':
                enemies.append(character)
        return characters, players, enemies

    @staticmethod
    def sort_initiative():
        characters.sort(key=lambda x: x.initiative, reverse=True)
        players.sort(key=lambda x: x.initiative, reverse=True)
        enemies.sort(key=lambda x: x.initiative, reverse=True)
        return characters, players, enemies

    @staticmethod
    def print_initiative():
        print('ИНИЦИАТИВА:')
        print(', '.join([character.get_name() + '(' + str(character.initiative) + ')' for character in characters]))

    def roll_dice(self, character_self, target, is_harm_target):
        dice = 0

        if self.test_mode:
            dice = random.randint(1, self.dice_range)
        elif not self.test_mode:
            dice = int(input('Введите результат броска:\n'))

        if dice == 1:
            return dice, 'fail'

        if dice >= character_self.crit_chance:
            return dice, 'crit'

        '''Если цель враждебная из броска вычитается штраф к попаданию по ней (уклонение)'''
        if is_harm_target:
            if isinstance(target, list):
                if character_self.hit_chance <= dice + character_self.hit_temp_bonus['harm']\
                        != character_self.crit_chance:
                    return dice, 1
            if character_self.hit_chance <= dice - target.hit_dodge + character_self.hit_temp_bonus['harm'] \
                    != character_self.crit_chance:
                return dice, 1
            else:
                return dice, 0
        else:
            if character_self.hit_chance <= dice + character_self.hit_temp_bonus['friendly'] \
                    != character_self.crit_chance:
                return dice, 1
            else:
                return dice, 0

    def actions(self, character_self):
        self.go_back = False
        action_index = character_self.choose_action()
        if character_self.get_rank() == 'common':
            if action_index == 0:  # AA
                self.auto_attack(character_self)
                character_self.reduce_action(3)

            elif action_index == -1:
                character_self.reduce_action(3)
                return

        else:
            if action_index == 0:       # AA
                if character_self.actions_count >= 2:
                    self.auto_attack(character_self)
                    character_self.reduce_action(2)
                elif character_self.actions_count == 1:
                    print('Персонаж не может использовать автоатаку, выберете другое действие')
                else:
                    return

            elif action_index == 1:     # spell
                if character_self.actions_count >= 2:
                    self.spell_choose(character_self)
                    character_self.reduce_action(2)
                elif character_self.actions_count == 1:
                    print('Персонаж не может использовать заклинания, выберете другое действие')
                else:
                    return

            elif action_index == 2:     # item
                if character_self.actions_count >= 1:
                    character_self.heal(5)
                    character_self.reduce_action(1)
                    print(character_self.get_name(), ' пьет зелье и излечивается на ', 5, ' ХП', sep='')
                else:
                    return

            elif action_index == -1:
                character_self.actions_count = 0
                return

        if character_self.actions_count > 0:
            self.actions(character_self)
        return

    def auto_attack(self, caster):
        target = self.choose_target(caster, enemies, players)
        if self.go_back:
            return
        dice, success = self.roll_dice(caster, target, True)

        if success == 0 or success == 'fail':
            print(caster.get_name(), ' d=', dice, ': промахивается', sep='')
            return
        else:
            dmg = caster.roll_aa_damage(success)
            dmg_print = caster.print_damage(caster.aa_damage_type, target, dmg, success, caster.armor_penetration)
            target.take_damage(dmg, caster.aa_damage_type, caster.armor_penetration)
            print(caster.get_name(), ' атакует ', target.get_name(), ' d=', dice, ':', ' (', *dmg_print, ')', sep='')

            return target

    def spell_choose(self, caster):
        index = caster.choose_magic()
        if index == -1:     # возврат назад в меню
            self.actions(caster)
            return
        spell = caster.abilities[index]['ability']
        target = self.spell_target(caster, spell)
        dice, success = self.roll_dice(caster, target, spell.harm)
        if success == 0:
            print(caster.get_name(), ' (d=', dice, ') промахивается', sep='')
            spell.is_used = True
            return
        elif success == 'fail':
            caster.add_cds(spell, 2)
            print(caster.get_name(), ' (d=', dice, ') критическая неудача', sep='')
        else:
            dmg = caster.roll_spell_damage(spell, success)
            spell.use_spell(target, caster, dmg, success)
            spell.description(target, caster, dmg, success, dice)
        return target

    def spell_target(self, character_self, spell):
        target = []
        if spell.harm:
            if spell.targets == 'single':
                target = self.choose_target(character_self, enemies, players)
                if self.go_back:
                    return
            elif spell.targets == 'AOE':
                target = enemies    # ТУТ ВСЕ НЕПРАВИЛЬНО
            else:
                tar_amount = spell.targets
                for i in range(tar_amount):
                    i = self.choose_target(character_self, enemies, players)
                    if self.go_back:
                        return
                    target.append(i)

        elif not spell.harm:
            if spell.targets == 'single':
                target = self.choose_target(character_self, players, enemies)
                if self.go_back:
                    return
            elif spell.targets == 'AOE':
                target = players
            else:
                tar_amount = spell.targets
                for i in range(tar_amount):
                    i = self.choose_target(character_self, players, enemies)
                    if self.go_back:
                        return
                    target.append(i)

        return target

    def choose_target(self, character_self, ens, pls):
        target = None
        if character_self.side == 'enemies':
            index = character_self.choose_target(pls)
            if index == -1:
                self.actions(character_self)
                self.go_back = True
                return
            target = pls[index]

        elif character_self.side == 'players':
            index = character_self.choose_target(ens)
            if index == -1:
                self.actions(character_self)
                self.go_back = True
                return
            target = ens[index]

        return target


game = Game()
