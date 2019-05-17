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
        self.targets = targets
        self.is_random = other.get('is_random', False)
        self.school = school
        self.crit_type = crit_type
        self.crit_strength = crit_strength
        self.action_cost = 2    # ДОДЕЛАТЬ
        self.is_used = False

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

    def reset_usage(self):
        self.is_used = False
        return self.is_used

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

    def use_spell(self, target, caster, dmg, success):
        dynamic_duration = self.dynamic_duration(caster, target, success)
        dynamic_cooldown = self.dynamic_cooldown(success)

        caster.add_durs(self, dynamic_duration)
        caster.add_cds(self, dynamic_cooldown)

        self.is_used = True

        if self.spell_id == 10001:   # Волшебная стрела
            target.take_damage(dmg, self.school)
            effect = Effects('hit_buff', 2, dynamic_duration, self, caster)
            caster.buffs.append(effect)
            effect.apply_effect(caster)
            print(caster.get_name(), 'получает +2 к попаданию на', dynamic_duration - 1, 'ход')

            return target, caster

        if self.spell_id == 31047:   # Подлый трюк
            target.take_damage(dmg, self.school)
            effect = Effects('stun', 0, dynamic_duration, self, caster)
            target.debuffs.append(effect)
            print(caster.get_name(), 'оглушает', target.get_name(), 'на',
                  'текущий' if dynamic_duration == 1 else dynamic_duration - 1, 'ход')
            return target, caster

        else:
            if self.targets == 'AOE':
                if self.harm:
                    for tar in target:
                        tar.take_damage(dmg, 'physic')
            else:
                if self.harm:
                    target.take_damage(dmg, 'physic')
                else:
                    target.heal(dmg)
            return target, caster

    def description(self, target, caster, dmg, success, dice):
        if self.harm:
            damage = caster.print_damage(self.school, target, dmg, success)
        else:
            if caster.damage_bonus > 0:
                damage = dmg - caster.damage_bonus, '+', caster.damage_bonus, '=', dmg
            else:
                damage = dmg, ''

        if self.targets == 'single':
            print(caster.get_name(), ' использует ', self.get_name(), ' на ', target.get_name(),
                  ' d=', dice, ':', ' (', *damage, ')', sep='')
        elif self.targets == 'AOE':
            print(caster.get_name(), ' использует ', self.get_name(), ' на ВСЕХ',
                  ' d=', dice, ':', ' (', *damage, ')', sep='')
        else:
            print(caster.get_name(), ' использует ', self.get_name(), ' на ',
                  ', '.join([tar.get_name() + ', ' for tar in target]), ' d=', dice, ':', ' (', *damage, ')', sep='')


class Effects:
    def __init__(self, mechanic, value, duration, from_spell, caster):
        self.mechanic = mechanic
        self.value = value
        self.duration = duration
        self.from_spell = from_spell
        self.caster = caster

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
            print('+' + str(self.value), 'попадание (' + self.from_spell.get_name() + ') -', self.duration, end='')
        if self.mechanic == 'stun':
            print('оглушение', self.duration, end='')
