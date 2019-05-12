from Base import *

turn = 1
is_game = 1

'''
11122
'''

game.test_mode = True
game.pre_start()

while is_game != 0:
    print('\nХОД', turn)
    for character in characters:
        print('\nХодит', character.get_name())
        game.actions(character)
        for effect in character.buffs:
            character.effect_reduce_duration(effect)    # МОЖНО ОБЪЕДЕНИТЬ
            character.remove_effect(effect)
        for effect in character.debuffs:
            character.effect_reduce_duration(effect)
            character.remove_effect(effect)
        character.reset_actions()
        game.death_check()
    print('\nСТАТИСТИКА:\n')
    game.get_stats()
    for character in characters:
        game.past_turn(character)

    turn += 1
    is_game = int(input('1 - продолжить\n0 - закончить\n'))
