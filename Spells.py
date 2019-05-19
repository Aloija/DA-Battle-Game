class Spells:
    def __init__(self, spell_id, name, damage, cooldown, duration, targets, school, crit_type,
                 crit_strength, **other):
        self.spell_id = spell_id
        self.name = name
        self.damage = damage
        self.cooldown = cooldown
        self.duration = duration
        self.targets = targets
        self.school = school
        self.crit_type = crit_type
        self.crit_strength = crit_strength

        self.harm = other.get('harm', True)
        self.effect = other.get('effect')
        self.initiative = other.get('initiative', False)
        self.is_random = other.get('is_random', False)
        self.armor_penetration = other.get('armor_penetration', False)
        self.is_next_action = other.get('is_next_action', False)

        self.action_cost = 2  # ДОДЕЛАТЬ
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
        dynamic_duration = self.duration + 1

        if self.initiative and character_self.initiative > target.initiative:
            dynamic_duration = self.duration

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

        self.is_used = True
        arm_pen = self.armor_penetration

        if self.spell_id == 10001:   # Волшебная стрела
            target.take_damage(dmg, self.school, arm_pen)
            effect = Effects(self.effect[0], dynamic_duration, self, value=self.effect[1], is_next_action=True,
                             caster=caster)
            caster.remove_identical_effect(effect)
            caster.buffs.append(effect)
            effect.apply_effect(caster)
            print(caster.get_name(), ' получает +', self.effect[1], ' к попаданию на слудующую атаку или способность',
                  sep='')

        if self.spell_id == 10003:  # Рассеивание
            choice = self.dispel(caster, target, 'magic')
            if choice != 0:
                if caster.side == target.side:
                    target.heal(dmg)
                    print(caster.get_name(), ' рассеивает ', choice.get_name(), ' c ', target.get_name(),
                          ' и исцеляет на ', dmg, sep='')
                else:
                    print(caster.get_name(), ' рассеивает ', choice.get_name(), ' c ', target.get_name(), sep='')
            else:
                print('нечего рассеивать.', sep='')
                return

        if self.spell_id == 31047:   # Подлый трюк
            target.take_damage(dmg, self.school, arm_pen)
            effect = Effects('stun', dynamic_duration, self, caster=caster)
            caster.remove_identical_effect(effect)
            target.debuffs.append(effect)
            print(caster.get_name(), 'оглушает', target.get_name(), 'на',
                  'текущий' if dynamic_duration == 1 else dynamic_duration - 1, 'ход')

        else:
            if self.targets == 'AOE':
                if self.harm:
                    for tar in target:
                        tar.take_damage(dmg, 'physic', arm_pen)
            else:
                if self.harm:
                    target.take_damage(dmg, 'physic', arm_pen)
                else:
                    target.heal(dmg)
                    effect = Effects('hit_buff', dynamic_duration, self, value=5)
                    caster.remove_identical_effect(effect)
                    caster.buffs.append(effect)
                    effect.apply_effect(caster)

        caster.add_durs(self, dynamic_duration)
        caster.add_cds(self, dynamic_cooldown)

        return target, caster

    def description(self, target, caster, dmg, success, dice):
        if self.harm:
            damage = caster.print_damage(self.school, target, dmg, success, self.armor_penetration)
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

    @staticmethod
    def dispel(caster, target, school):
        spells = []
        i = 1
        print('Выберете какой эффект рассеять:')
        if caster.side == target.side:
            for effect in target.debuffs:
                if effect.school == school:
                    if effect.from_spell not in spells:  # Выбор заклинания, чьи эффекты рассеять
                        spells.append(effect.from_spell)
                        print(i, ': ', effect.from_spell.get_name())
                        i += 1
        else:
            for effect in target.buffs:
                if effect.school == school:
                    if effect.from_spell not in spells:  # Выбор заклинания, чьи эффекты рассеять
                        spells.append(effect.from_spell)
                        print(i, ': ', effect.from_spell.get_name())
                        i += 1

        if len(spells) == 0:
            return 0
        choice = spells[int(input()) - 1]
        effect_caster = None

        if caster.side == target.side:
            for effect in target.debuffs:
                if effect.from_spell == choice:
                    effect_caster = effect.caster
                    target.set_effects_to_0(effect)
        else:
            for effect in target.buffs:
                if effect.from_spell == choice:
                    effect_caster = effect.caster
                    target.set_effects_to_0(effect)

        for now in effect_caster.abilities:
            if choice == now['ability']:
                now['duration'] = 0
        return choice


class Effects:
    def __init__(self, mechanic, duration, from_spell, **other):
        self.mechanic = mechanic
        self.value = other.get('value', 0)
        self.duration = duration
        self.from_spell = from_spell
        self.caster = other.get('caster', None)
        self.target = other.get('target', None)
        self.school = from_spell.school
        self.is_next_action = other.get('is_next_action', False)

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
