import random


class Unit:
    def __init__(self, name, hp, damage, damage_bonus, defence, spells_list, **other):
        self.__name = name
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.damage_bonus = damage_bonus    # МОЖНО ВЫПИЛИТЬ
        self.defence = defence
        self.hit_chance = 10    # БОНУС СДЕЛАТЬ
        self.__base_hit = 10
        self.crit_chance = 20
        self.__base_crit = 20   # БОНУС СДЕЛАТЬ
        self.spells_list = spells_list  # СДЕЛАТЬ ПО ID
        self.abilities = []
        self.actions = ['Автоатака', 'Способность', 'Предмет']
        self.debuffs = []
        self.buffs = []
        self.auras = []
        self.initiative = 0
        self.actions_count = 300  # AA - 2, spell - 2, item - 1, free_spell - 1
        self.damage_type = other.get('damage_type', 'physic')
        self.damage_reduce = {'magic': 0, 'physic': 0}
        self.hit_dodge = other.get('hit_dodge', 0)
        self.damage_harm_bonus = {'harm': 0, 'frendly': 0}
        self.hit_harm_bonus = {'harm': 0, 'frendly': 0}

    def __str__(self):
        return '(%r/%r) %r: %r\n%r' % (self.hit_chance, self.crit_chance, self.__name, self.hp, self.damage)

    def get_rank(self):
        pass

    def get_name(self):
        return self.__name

    def get_hp(self):
        return self.hp

    def get_damage(self):
        d_min = self.damage[0] + self.damage_bonus
        d_max = self.damage[1] + self.damage_bonus
        return d_min, '-', d_max

    def get_defence(self):
        return self.defence

    def roll_damage(self, success, _from, game):
        dmg = random.randint(self.damage[0], self.damage[1]) + self.damage_bonus
        if _from == 'AA':
            if success == 'crit':
                dmg *= game.crit_modifier

        return int(dmg)

    def take_damage(self, dmg, damage_type):
        if damage_type == 'magic':
            dmg = dmg - round(dmg * self.damage_reduce['magic'])
        elif damage_type == 'physic':
            dmg = dmg - round(dmg * self.damage_reduce['physic'])
        else:
            dmg = dmg
        if dmg >= self.defence:
            dmg = dmg - self.defence
            self.hp -= dmg
        if self.hp < 0:
            self.hp = 0
        return self.hp

    def print_damage(self, damage_type, target, dmg, success):
        if self.damage_bonus > 0:
            damage = dmg - self.damage_bonus, '+', self.damage_bonus
        else:
            damage = dmg, ''

        if success == 'crit':
            crit = ', Критический'
        else:
            crit = ''

        if isinstance(target, list):
            if len(target) > 1:
                damage_print = damage, crit
                return damage_print
            else:
                tar = target[0]
        else:
            tar = target

        if damage_type == 'magic':
            if tar.damage_reduce['magic'] > 0:
                damage_reduce = round(tar.damage_reduce['magic'] * 100)
            else:
                damage_reduce = ''
        else:
            if tar.damage_reduce['physic'] > 0:
                damage_reduce = round(tar.damage_reduce['physic'] * 100)
            else:
                damage_reduce = ''

        if damage_reduce != '':
            damage_total = round(dmg - dmg * (damage_reduce/100) - tar.defence)
            damage_reduce = '-', str(damage_reduce) + '%'
        else:
            damage_total = dmg - tar.defence

        if damage_total > tar.defence:
            if tar.defence > 0:
                defence = '-', tar.defence
            elif tar.defence < 0:
                defence = '+', tar.defence * -1
            else:
                defence = ''
        else:
            damage_print = 'урон(', damage_total, ') не пробивает броню.'
            return damage_print

        if dmg == damage_total:
            damage_print = dmg, crit
        else:
            damage_print = *damage, *damage_reduce, *defence, '=', damage_total, crit

        return damage_print

    def roll_dice(self):
        dice = random.randint(1, 2)
        if dice >= self.crit_chance:
            return dice, 'crit'
        elif self.hit_chance <= dice < self.crit_chance:
            return dice, 1
        else:
            return dice, 0

    def set_abilities(self):
        for spell in self.spells_list:
            self.abilities.append({'ability': spell, 'cooldown': -1, 'duration': -1})

    def reset_actions(self):
        self.actions_count = 3
        return self.actions_count

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
        for spell in self.spells_list:
            print(str(i), ': ', spell.get_name(), sep='')
            i += 1
        print('0: Главное меню')
        index = int(input()) - 1
        if index != -1 and self.abilities[index]['cooldown'] > -1:
            print(self.abilities[index]['ability'].name, 'на перезарядке\n')
            index = self.choose_magic()
        return index

    @staticmethod
    def choose_target(ens):
        i = 1
        print('Выберете цель:')
        for enemy in ens:
            if enemy.get_hp() != 0:
                print(str(i), ': ', enemy.get_name(), ' (', enemy.get_hp(), ' ХП)', sep='')
                i += 1
        print('0: Главное меню')
        index = int(input()) - 1
        return index

    '''                         Эффекты                        '''

    def add_action(self, cost):
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

    def heal(self, dmg):
        self.hp += dmg
        if self.hp > self.max_hp:
            self.set_hp_to_max()
        return self.hp

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

    def set_effect_to_0(self, effect):
        if effect in self.buffs:
            effect.duration = 0
        if effect in self.debuffs:
            effect.duration = 0
        if effect in self.auras:
            effect.duration = 0
        return self

    '''Проверка всех эффектов, которые баффают для след. атаки'''
    

class Player(Unit):
    def __init__(self, name, hp, damage, damage_bonus, defence, characteristics, hit_chance, crit_chance, spells_list,
                 c_class, **other):
        Unit.__init__(self, name, hp, damage, damage_bonus, defence, spells_list)
        self.characteristics = characteristics
        self.hit_chance = hit_chance
        self.base_hit = self.hit_chance
        self.crit_chance = crit_chance
        self.base_crit = self.crit_chance
        self.c_class = c_class
        self.side = 'players'
        self.hp = self.hp + (self.characteristics['stamina'] * 10)
        self.max_hp = self.hp
        self.damage_type = other.get('damage_type', 'physic')

        if self.c_class == 'warrior':
            self.damage[0] += self.characteristics['strength']
            self.damage[1] += self.characteristics['strength']
        elif self.c_class == 'rogue':
            self.damage[0] += self.characteristics['agility']
            self.damage[1] += self.characteristics['agility']
        else:
            self.damage[0] += self.characteristics['intelligence']
            self.damage[1] += self.characteristics['intelligence']

    def get_stats(self):
        if self.hp > 0:
            print(self.get_name(), sep='', end='')
            print(': ', end='')
            for effect in self.buffs:
                effect.get_stats()
            for effect in self.debuffs:
                effect.get_stats()
            print('\n(', self.hit_chance, '/', self.crit_chance, ')', ' Здоровье: ', self.get_hp(), sep='')
            print('Защита:', self.get_defence())
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
    def __init__(self, name, hp, damage, damage_bonus, defence, spells_list, rank, **other):
        Unit.__init__(self, name, hp, damage, damage_bonus, defence, spells_list)
        self.rank = rank
        self.side = 'enemies'
        self.actions = ['Автоатака', 'Способность']
        self.damage_type = other.get('damage_type', 'physic')

        if self.rank == 'elite':
            self.hit_chance = 5
            self.base_hit = self.hit_chance
        elif self.rank == 'rare':
            self.hit_chance = 7
            self.base_hit = self.hit_chance
        else:
            self.actions = ['Автоатака']

    def get_rank(self):
        return self.rank

    def get_stats(self):
        if self.hp > 0:
            if self.rank == 'rare' or self.rank == 'elite':
                print(self.get_name(), sep='', end='')
                print(': ', end='')
                for effect in self.buffs:
                    effect.get_stats()
                for effect in self.debuffs:
                    effect.get_stats()
                print('\n(', self.hit_chance, '/', self.crit_chance, ')', ' Здоровье: ', self.get_hp(), sep='')
                print('Защита:', self.get_defence())
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
                print(self.get_name(), ': ', self.get_hp(), sep='', end='')
                for effect in self.buffs:
                    effect.get_stats()
                for effect in self.debuffs:
                    effect.get_stats()
                print('\n')

        if self.hp <= 0:
            print(self.get_name(), sep='', end='')
            print(': Х_х\n', end='')
            print('')
