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

    player_home = player_planets[-1]
    player_planets = player_planets[:-1]

    # Check all non-home owned planets for spare ships starting with the lowest tier
    for planet in player_planets:
        if (planet.growth_rate * modifier_planet_spares) < planet.num_ships:
            transfer_size = planet.num_ships - (planet.growth_rate * modifier_planet_defense)

            return issue_order(state, planet.ID, player_home.ID, transfer_size)

    # No planet has spare ships
    return False


def capture_neighbors(state):
    """
        Focus on securing close planets

    """

    # Distance is how far from home_planet to consider
    modifier_neighbor_distance   = 20
    # How much are more productive planets valued; how much more is a 2-ship planet prefered over a 1-ship
    modifier_neighbor_production = 2

    # How much to consider a planet's defense
    # A higher value means that we need to outnumber them by more before considering
    modifier_neighbor_defense    = 1.1

    home_planet = max(state.my_planets(), key=lambda t: t.num_ships)

    # Check for any fleets that are already capturing
    targeted_planets = set( [ fleet.destination_planet for fleet in state.my_fleets() ] )

    # Calculates how many ships will encountered by a friendly fleet departing from source at destination
    def expected_fleet(source, destination):
        travel_time = state.distance(source.ID, destination.ID)
        return (destination.num_ships + (destination.growth_rate * travel_time)) * modifier_neighbor_defense

    def planet_val(planet):
        # Can it be captured with our fleet?
        if (modifier_neighbor_defense * planet.num_ships) > home_planet.num_ships:
            return -1

        # Larger distances, less desireable
        dist_val = modifier_neighbor_distance / state.distance(home_planet.ID, planet.ID)
        prod_val = modifier_neighbor_production * planet.growth_rate

        # Defense of planets when ships would arrive at location
        defs_val = home_planet.num_ships / expected_fleet(home_planet, planet)

        return (dist_val + prod_val + defs_val)
    # list of neighbors sorted by decreasing planet value
    neighbor_planets = sorted(state.not_my_planets(), key=lambda t: planet_val(t), reverse=True)

    for neighbor in neighbor_planets:
        if neighbor.ID not in targeted_planets:
            return issue_order(state, home_planet.ID, neighbor.ID, expected_fleet(home_planet, neighbor))

    return False
