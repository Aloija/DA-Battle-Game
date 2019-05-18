import random


class Unit:
    def __init__(self, name, hp, damage_bonus, armor, spells_list, c_class, **other):
        self.__name = name
        self.hp = hp
        self.max_hp = hp
        self.c_class = c_class

        self.spells_list = spells_list
        self.abilities = []
        self.debuffs = []
        self.buffs = []
        self.auras = []

        self.hit_chance = 10
        self.crit_chance = 20
        self.__base_hit = self.hit_chance
        self.__base_crit = self.crit_chance
        self.hit_temp_bonus = {'harm': 0, 'friendly': 0}

        self.damage_bonus = damage_bonus
        self.aa_damage_type = other.get('damage_type', 'physic')
        self.damage_percent_bonus = {'harm': 0, 'friendly': 0}
        self.damage_flat_bonus = {'harm': 0, 'friendly': 0}
        self.armor_penetration = False

        self.armor = armor
        self.barrier = other.get('barrier', 0)
        self.defence = other.get('defence', 0)
        self.damage_reduce = {'magic': 0, 'physic': 0}
        self.hit_dodge = other.get('hit_dodge', 0)

        self.initiative = 0
        self.actions = ['Автоатака', 'Способность', 'Предмет']
        self.actions_count = 300  # AA - 2, spell - 2, item - 1, free_spell - 1

    def get_rank(self):
        pass

    def set_damage(self, weapons_list):
        pass

    def safe_roll(self, threshold, characteristic):
        pass

    def get_name(self):
        return self.__name

    def set_abilities(self):
        for spell in self.spells_list:
            self.abilities.append({'ability': spell, 'cooldown': -1, 'duration': -1})

    def reset_actions(self):
        self.actions_count = 3
        return self.actions_count

    def reset_spell_usage(self):
        for spell in self.abilities:
            spell['ability'].reset_usage()

    @staticmethod
    def print_damage(damage_type, target, dmg, success, arm_pen):
        damage = dmg, ''

        if arm_pen:
            arm_pen = ', Пробивающий'
        else:
            arm_pen = ''

        if success == 'crit':
            crit = ', Критический'
        else:
            crit = ''

        if isinstance(target, list):
            damage_print = *damage, *crit, arm_pen
            return damage_print

        if damage_type == 'magic':
            if target.damage_reduce['magic'] > 0:
                damage_reduce = round(target.damage_reduce['magic'] * dmg)
            else:
                damage_reduce = ''
        else:
            if target.damage_reduce['physic'] > 0:
                damage_reduce = round(target.damage_reduce['physic'] * dmg)
            else:
                damage_reduce = ''

        if damage_reduce != '':
            damage_total = round(dmg - damage_reduce)
            damage_reduce = '-', str(damage_reduce)
        else:
            damage_total = dmg

        if target.barrier == 0 and target.defence == 0:
            if damage_total < target.armor and not arm_pen:
                damage_print = 'урон (', *damage, *damage_reduce, '=', damage_total, crit, ') не пробивает броню)'
                return damage_print

        if dmg == damage_total:
            damage_print = dmg, crit, arm_pen
        else:
            damage_print = *damage, *damage_reduce, '=', damage_total, crit, arm_pen

        return damage_print

    '''                         Эффекты                        '''

    def take_damage(self, dmg, damage_type, arm_pen):
        if damage_type == 'magic':
            dmg -= round(dmg * self.damage_reduce['magic'])
        elif damage_type == 'physic':
            dmg -= round(dmg * self.damage_reduce['physic'])

        if self.barrier > 0:
            dmg, self.barrier = dmg - self.barrier, self.barrier - dmg
            if self.barrier < 0:
                self.barrier = 0

        if self.defence > 0:
            if dmg > 0:
                dmg, self.defence = dmg - self.defence, self.defence - dmg
                if self.defence < 0:
                    self.defence = 0

        if not arm_pen:
            if dmg >= self.armor:
                dmg -= self.armor
            else:
                dmg = 0

        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0

        return self.hp

    def heal(self, dmg):
        self.hp += dmg
        if self.hp > self.max_hp:
            self.set_hp_to_max()
        return self.hp

    def reduce_action(self, cost):
        self.actions_count -= cost
        return self.actions_count

    def add_cds(self, spell, cooldown):
        for now in self.abilities:
            if now['ability'] == spell:
                now['cooldown'] += cooldown
        return self.abilities

    def cd_reduce(self, spell):
        for now in self.abilities:
            if now['ability'] == spell:
                if now['cooldown'] > -1 and now['duration'] == -1:
                    now['cooldown'] -= 1
        return self.abilities

    def add_durs(self, spell, duration):
        for now in self.abilities:
            if now['ability'] == spell:
                now['duration'] += duration
        return self.abilities

    def dur_reduce(self, spell):
        for now in self.abilities:
            if now['ability'] == spell:
                if now['duration'] > -1:
                    now['duration'] -= 1
        return self.abilities

    def set_hp_to_max(self):
        self.hp = self.max_hp

    def buff_hit(self, value):
        self.hit_chance -= value
        return self.hit_chance

    def debuff_hit(self, value):
        self.hit_chance += value
        return self.hit_chance

    def effect_reduce_duration(self, effect):
        if effect in self.buffs:
            effect.dur_reduce()
        if effect in self.debuffs:
            effect.dur_reduce()

        self.remove_effect(effect)

        return self

    def remove_effect(self, effect):
        if effect.duration == 0:
            if effect in self.buffs:
                effect.remove_effect(self)
                self.buffs.remove(effect)
            if effect in self.debuffs:
                self.debuffs.remove(effect)

        return self

    def on_time_effects(self):
        pass

    def set_effects_to_0(self, effect):
        if effect in self.buffs:
            effect.duration = 0
        if effect in self.debuffs:
            effect.duration = 0
        if effect in self.auras:
            effect.duration = 0

        self.remove_effect(effect)

        return self

    def remove_identical_effect(self, effect):
        for item in self.buffs:
            if effect.mechanic == item.mechanic:
                for spell in self.abilities:
                    if spell['ability'].spell_id == item.from_spell.spell_id:
                        spell['duration'] = -1
                self.set_effects_to_0(item)
                return
        for item in self.debuffs:
            if effect.mechanic == item.mechanic:
                for spell in self.abilities:
                    if spell['ability'].spell_id == item.from_spell.spell_id:
                        spell['duration'] = -1
                self.set_effects_to_0(item)
                return
        for item in self.auras:
            if effect.mechanic == item.mechanic:
                for spell in self.abilities:
                    if spell['ability'].spell_id == item.from_spell.spell_id:
                        spell['duration'] = -1
                self.set_effects_to_0(item)

    '''                         Действия                   '''

    def choose_action(self):
        i = 1
        for effect in self.debuffs:
            if effect.mechanic == 'stun':
                print(self.__name, 'пропускает ход (оглушение)')
                index = -1
                return index
        print('\nВыберете действие:')
        for action in self.actions:
            print(str(i), ': ', action, sep='')
            i += 1
        print('0: Пропустить ход')
        index = int(input()) - 1
        return index

    def choose_magic(self):
        i = 1
        print('Выберте способность:')
        for spell in self.abilities:
            print(str(i), ': ', spell['ability'].get_name(), ', кд - ',
                  spell['cooldown'] if spell['cooldown'] > 0 else 'нет', sep='')
            i += 1
        print('0: Главное меню')
        index = int(input()) - 1
        if index != -1 and self.abilities[index]['cooldown'] > -1:
            print(self.abilities[index]['ability'].get_name(), 'на перезарядке\n')
            index = self.choose_magic()
        if index != -1 and self.abilities[index]['ability'].is_used:
            print('Вы не можете повторно использовать', self.abilities[index]['ability'].get_name(), '\n')
            index = self.choose_magic()
        return index

    @staticmethod
    def choose_target(ens):
        i = 1
        print('Выберете цель:')
        for enemy in ens:
            if enemy.hp != 0:
                print(str(i), ': ', enemy.get_name(), ' (', enemy.hp, ' ХП)', sep='')
                i += 1
        print('0: Главное меню')
        index = int(input()) - 1
        return index
    

class Player(Unit):
    def __init__(self, name, hp, damage_bonus, armor, hit_chance, crit_chance, spells_list, c_class,
                 weapon, characteristics):
        Unit.__init__(self, name, hp, damage_bonus, armor, spells_list, c_class)
        self.characteristics = characteristics
        self.hit_chance = hit_chance
        self.crit_chance = crit_chance
        self.weapon = weapon
        self.hp = self.hp + (self.characteristics['stamina'] * 10)
        self.damage = {'physic': [0, 0], 'magic': [0, 0]}
        self.side = 'players'

    def set_damage(self, weapons_list):
        if self.weapon in weapons_list['strength']:
            for i in range(2):
                self.damage['physic'][i]\
                    = weapons_list['strength'][self.weapon][i] + self.characteristics['strength'] + self.damage_bonus
        elif self.weapon in weapons_list['agility']:
            for i in range(2):
                self.damage['physic'][i]\
                    = weapons_list['agility'][self.weapon][i] + self.characteristics['agility'] + self.damage_bonus

        if self.c_class == 'mage':
            if self.weapon in weapons_list['wisdom']:
                for i in range(2):
                    self.damage['magic'][i]\
                        = weapons_list['wisdom'][self.weapon][i] + self.characteristics['wisdom'] + self.damage_bonus
                    self.damage['physic'][i]\
                        = weapons_list['wisdom'][self.weapon][i] + self.characteristics['wisdom'] + self.damage_bonus
                    self.aa_damage_type = 'magic'
            else:
                self.damage['magic'] = [self.characteristics['wisdom'], self.characteristics['wisdom']]

    def get_damage(self):
        phys_d_min = self.damage['physic'][0]
        phys_d_max = self.damage['physic'][1]
        mag_d_min = self.damage['magic'][0]
        mag_d_max = self.damage['magic'][1]

        if self.c_class == 'mage':
            if self.damage['physic'] != self.damage['magic']:
                return 'физ:', phys_d_min, '-', phys_d_max, 'маг:', mag_d_min
            else:
                return mag_d_min, '-', mag_d_max
        else:
            return phys_d_min, '-', phys_d_max

    def roll_aa_damage(self, success):
        if self.aa_damage_type == 'magic':
            dmg = random.randint(self.damage['magic'][0], self.damage['magic'][1])
        else:
            dmg = random.randint(self.damage['physic'][0], self.damage['physic'][1])
        if success == 'crit':
            dmg *= 1.5
        return int(dmg)

    def roll_spell_damage(self, spell, success):
        if spell.school == 'magic':
            dmg = random.randint(self.damage['magic'][0], self.damage['magic'][1])
        else:
            dmg = random.randint(self.damage['physic'][0], self.damage['physic'][1])

        if spell.harm:
            dmg += self.damage_flat_bonus['harm'] + dmg * self.damage_percent_bonus['harm']
        else:
            dmg += self.damage_flat_bonus['friendly'] + dmg * self.damage_percent_bonus['friendly']

        if success == 1:
            dmg = round(dmg * spell.damage)
        if success == 'crit':
            if spell.crit_type == 'damage':
                dmg = round(dmg * spell.crit_strength)
            else:
                dmg = round(dmg * spell.damage)

        return dmg

    def safe_roll(self, threshold, characteristic):
        characteristic = sorted(characteristic, key=lambda x: self.characteristics[x])
        dice = random.randint(1, 20) + characteristic[0]
        if dice >= threshold:
            success = 1
        else:
            success = 0

        return dice, success

    def get_stats(self):
        if self.defence > 0:
            defence = '[', self.defence, ']'
        else:
            defence = ''
        if self.barrier > 0:
            barrier = '(', self.barrier, ')'
        else:
            barrier = ''

        if self.hp > 0:
            print(self.get_name(), sep='', end='')
            print(': ', end='')
            for effect in self.buffs:
                effect.get_stats()
            for effect in self.debuffs:
                effect.get_stats()
            print('\n(', self.hit_chance, '/', self.crit_chance, ')', ' Здоровье: ', self.hp, *defence, *barrier,
                  sep='')
            print('Защита:', self.armor)
            print('Урон:', *self.get_damage())

            for now in self.abilities:
                if now['cooldown'] > 0:
                    if now['duration'] > 0:
                        print(now['ability'].get_name(), ': ', str(now['duration']), '+', str(
                            now['cooldown']), sep='')
                    else:
                        print(now['ability'].get_name(), ': ', str(now['cooldown']), sep='')
                elif now['cooldown'] == 0:
                    print(now['ability'].get_name(), ': ОТКАЧЕНО', sep='')
            print('')

        if self.hp <= 0:
            print(self.get_name(), sep='', end='')
            print(': Х_х\n', end='')
            print('')


class Enemy(Unit):
    def __init__(self, name, hp, damage, damage_bonus, armor, spells_list, rank, c_class, **other):
        Unit.__init__(self, name, hp, damage_bonus, armor, spells_list, c_class)
        self.rank = rank
        self.actions = ['Автоатака', 'Способность']
        self.damage = [damage[0] + self.damage_bonus, damage[1] + self.damage_bonus]
        self.side = 'enemies'

        if self.rank == 'elite':
            self.hit_chance = 5
        elif self.rank == 'rare':
            self.hit_chance = 7
        else:
            self.actions = ['Автоатака']

    def get_damage(self):
        d_min = self.damage[0]
        d_max = self.damage[1]
        return d_min, '-', d_max

    def roll_aa_damage(self, success):
        dmg = random.randint(self.damage[0], self.damage[1])
        if success == 'crit':
            dmg *= 1.5
        return int(dmg)

    def roll_spell_damage(self, spell, success):
        if spell.school == 'magic':
            dmg = random.randint(self.damage[0], self.damage[1])
        else:
            dmg = random.randint(self.damage[0], self.damage[1])

        if spell.harm:
            dmg += self.damage_percent_bonus['harm']
        else:
            dmg += self.damage_percent_bonus['friendly']

        if success == 1:
            dmg = round(dmg * spell.damage)
        if success == 'crit':
            if spell.crit_type == 'damage':
                dmg = round(dmg * spell.crit_strength)
            else:
                dmg = round(dmg * spell.damage)

        return dmg

    def safe_roll(self, threshold, characteristic):
        dice = random.randint(1, 20)
        if dice >= threshold:
            success = 1
        else:
            success = 0

        return dice, success

    def get_stats(self):
        if self.defence > 0:
            defence = '[', self.defence, ']'
        else:
            defence = ''
        if self.barrier > 0:
            barrier = '(', self.barrier, ')'
        else:
            barrier = ''

        if self.hp > 0:
            if self.rank == 'rare' or self.rank == 'elite':
                print(self.get_name(), sep='', end='')
                print(': ', end='')
                for effect in self.buffs:
                    effect.get_stats()
                for effect in self.debuffs:
                    effect.get_stats()
                print('\n(', self.hit_chance, '/', self.crit_chance, ')', ' Здоровье: ', self.hp, *defence, *barrier,
                      sep='')
                print('Защита:', self.armor)
                print('Урон:', *self.get_damage())
                for now in self.abilities:
                    if now['cooldown'] > 0:
                        if now['duration'] > 0:
                            print(now['ability'].get_name(), ': ', str(now['duration']), '+', str(
                                now['cooldown']), sep='')
                        else:
                            print(now['ability'].get_name(), ': ', str(now['cooldown']), sep='')
                    elif now['cooldown'] == 0:
                        print(now['ability'].get_name(), ': ОТКАЧЕНО', sep='')
                print('')
            else:
                print('(', self.hit_chance, '/', self.crit_chance, ')', self.get_name(), ': ', self.hp, *defence,
                      *barrier, sep='', end='')
                for effect in self.buffs:
                    effect.get_stats()
                for effect in self.debuffs:
                    effect.get_stats()
                print('\n')

        if self.hp <= 0:
            print(self.get_name(), sep='', end='')
            print(': Х_х\n', end='')
            print('')
