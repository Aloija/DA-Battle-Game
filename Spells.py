class Spells:
    def __init__(self, spell_id, name, damage, cooldown, duration, effect_type, targets, school, crit_type,
                 crit_strength, **other):
        self.spell_id = spell_id
        self.name = name
        self.damage = damage
        self.cooldown = cooldown
        self.duration = duration
        self.harm = other.get('harm', True)
        self.effect_type = effect_type
        self.targets = targets      # Single, AOE, Number of
        self.is_random = other.get('is_random', False)
        self.school = school    # magic, physic
        self.crit_type = crit_type
        self.crit_strength = crit_strength
        self.action_cost = 2    # ДОДЕЛАТЬ

    def __str__(self):
        return self.name

    def get_damage(self):
        return self.damage

    def get_name(self):
        return self.name

    def get_cd(self):
        return self.cooldown

    def get_dur(self):
        return self.duration

    def generate_damage(self, character_self, success):
        if success == 1:
            dmg = round(character_self.roll_damage(success, 'spell', self.school) * self.damage)
            return dmg
        elif success == 'crit':
            if self.crit_type == 'damage':
                dmg = round(character_self.roll_damage(success, 'spell', self.school) * self.crit_strength)
            else:
                dmg = round(character_self.roll_damage(success, 'spell', self.school) * self.damage)
            return dmg

    def dynamic_duration(self, character_self, target, success):
        if self.targets == 'single':
            if self.effect_type == 'buff_active':
                dynamic_duration = self.duration + 1
            elif self.effect_type == 'debuff':
                if character_self.initiative > target.initiative:
                    dynamic_duration = self.duration
                else:
                    dynamic_duration = self.duration + 1
            else:
                dynamic_duration = self.duration + 1
        else:
            dynamic_duration = self.duration + 1

        if success == 'crit':
            if self.crit_type == 'duration':
                dynamic_duration += self.crit_strength

        return dynamic_duration

    def dynamic_cooldown(self, success):
        dynamic_cooldown = self.cooldown + 1
        if success == 'crit':
            if self.crit_type == 'cooldown':
                dynamic_cooldown -= self.crit_strength
        return dynamic_cooldown

    def use_spell(self, target, character_self, dmg, success):
        dynamic_duration = self.dynamic_duration(character_self, target, success)
        dynamic_cooldown = self.dynamic_cooldown(success)

        character_self.add_durs(self, dynamic_duration)
        character_self.add_cds(self, dynamic_cooldown)

        if self.spell_id == 10001:   # Волшебная стрела
            target.take_damage(dmg, self.school)
            character_self.buffs.append(Effects(('попадание (' + self.get_name() + ')'), 'hit_buff',
                                                2, dynamic_duration, self.spell_id))
            print(character_self.get_name(), 'получает +2 к попаданию на', dynamic_duration - 1, 'ход')
            for effect in character_self.buffs:
                if effect.from_spell == self.spell_id:
                    effect.apply_effect(character_self)

            return target, character_self

        if self.spell_id == 31047:   # Подлый трюк
            target.take_damage(dmg, self.school)
            target.debuffs.append(Effects(('оглушение (' + self.get_name() + ')'), 'stun',
                                          0, dynamic_duration, self.spell_id))
            print(character_self.get_name(), 'оглушает', target.get_name(), 'на',
                  'текущий' if dynamic_duration == 1 else dynamic_duration - 1, 'ход')
            return target, character_self

        else:
            if self.harm:
                target.take_damage(dmg, 'physic')

            else:
                target.heal(dmg)
            return target, character_self

    def description(self, target, character_self, dmg, success, dice):
        if self.harm:
            damage = character_self.print_damage(self.school, target, dmg, success)
        else:
            if character_self.damage_bonus > 0:
                damage = dmg - character_self.damage_bonus, '+', character_self.damage_bonus, '=', dmg
            else:
                damage = dmg, ''

        if self.targets == 'single':
            print(character_self.get_name(), ' использует ', self.get_name(), ' на ', target[0].get_name(),
                  ' d=', dice, ':', ' (', *damage, ')', sep='')
        elif self.targets == 'AOE':
            print(character_self.get_name(), ' использует ', self.get_name(), ' на ВСЕХ',
                  ' d=', dice, ':', ' (', *damage, ')', sep='')
        else:
            print(character_self.get_name(), ' использует ', self.get_name(), ' на ',
                  ', '.join([tar.get_name() + ', ' for tar in target]), ' d=', dice, ':', ' (', *damage, ')', sep='')


class Effects:
    def __init__(self, name, mechanic, value, duration, from_spell):
        self.name = name
        self.mechanic = mechanic
        self.value = value
        self.duration = duration
        self.from_spell = from_spell

    def get_name(self):
        return self.name

    def dur_reduce(self):
        if self.duration > 0:
            self.duration -= 1
        return self.duration

    def apply_effect(self, target):
        if self.mechanic == 'hit_buff':
            target.buff_hit(self.value)

    def remove_effect(self, self_character):
        if self.mechanic == 'hit_buff':
            self_character.debuff_hit(self.value)

    def get_stats(self):
        if self.mechanic == 'hit_buff':
            print('+' + str(self.value), self.get_name(), '-', self.duration, end='')
        if self.mechanic == 'stun':
            print(self.get_name(), self.duration, end='')
