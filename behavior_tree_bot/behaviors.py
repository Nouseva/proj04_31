import sys
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def consolidate_ships(state):
    """
        Gathers ships from lower tier planets to higher tier planets

        Tries to keep a base level defense proportional to planet tier
    """

    # Keep a base of X times the planet's production in ships
    modifier_planet_defense = 10
    # X times the planet's production is an excess of ships
    modifier_planet_spares  = 15

    # Check we have more than one fleet to consider
    player_planets = sorted(state.my_planets(), key=lambda t: t.growth_rate)

    if len(player_planets) < 2:
        return False

    player_home = player_planets[0]
    player_planets = player_planets[1::-1]

    # Check all non-home owned planets for spare ships starting with the lowest tier
    for planet in player_planets:
        if (planet.growth_rate * modifier_planet_spares) < planet.num_ships:
            transfer_size = planet.num_ships - (planet.growth_rate * modifier_planet_defense)

            return issue_order(state, planet.ID, player_home.ID, transfer_size)

    # No planet has spare ships
    return False
