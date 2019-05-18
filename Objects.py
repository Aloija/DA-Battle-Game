from Units import *
from Spells import *

magic_bolt = Spells(spell_id=10001, name='Волшебная стрела', damage=1, cooldown=3, duration=1,
                    effect_type='buff_active', targets='single', school='magic', crit_type='damage', crit_strength=2)
spell_2 = Spells(spell_id=31047, name='Подлый трюк', damage=1.5, cooldown=3, duration=1, effect_type='debuff',
                 targets='single', school='physic', crit_type='damage', crit_strength=2)
spell_3 = Spells(spell_id=21233, name='Аура боли', damage=0.5, cooldown=3, duration=0, effect_type=None, targets='AOE',
                 school='physic', crit_type='duration', crit_strength=1)
heal = Spells(spell_id=10002, name='Исцеление', damage=1, cooldown=1, duration=0, effect_type=None, targets='single',
              school='magic', crit_type='damage', crit_strength=2, harm=False)

test_spells = [magic_bolt, spell_2, spell_3, heal]


'''                     ПЕРСОНАЖИ        '''

player_1 = Player(name='Мэйрис', hp=200, damage_bonus=0, armor=-2, characteristics={'stamina': 2, 'strength': 0,
                                                                                    'agility': 4, 'intelligence': 1,
                                                                                    'wisdom': 0, 'observation': 3},
                  hit_chance=1, crit_chance=20, spells_list=test_spells, c_class='rogue', weapon='ranged')

player_2 = Player(name='Хекс', hp=20, damage_bonus=0, armor=2, characteristics={'stamina': 3, 'strength': 3,
                                                                                'agility': 1, 'intelligence': 0,
                                                                                'wisdom': 0, 'observation': 1},
                  hit_chance=10, crit_chance=20, spells_list=test_spells, c_class='warrior', weapon='dual_swords')


enemy_1 = Enemy(name='Карамелька', hp=30, damage=[12, 17], damage_bonus=0, armor=1, spells_list=test_spells,
                rank='common', c_class='demon')
enemy_2 = Enemy(name='Разикаль', hp=300, damage=[9, 14], damage_bonus=5, armor=50, spells_list=test_spells,
                rank='elite', damage_type='magic', c_class='dragon')


weapons = {'wisdom': {'staff': [5, 10]},
           'strength': {'shield': [3, 8], 'two_handed': [10, 15], 'duals_swords': [9, 14], 'one_sword': [4, 9]},
           'agility': {'dual_daggers': [7, 12], 'ranged': [8, 13], 'one_dagger': [3, 8]}}

players = []
enemies = []
characters = [player_1, enemy_2]
players_corpses = []
enemies_corpses = []
