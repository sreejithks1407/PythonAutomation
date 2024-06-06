# -*- coding: utf-8 -*-
"""
Champions League Draw Algorithm

@author: Sreejith
"""

import pandas as pd
import numpy as np

# 2021 results of group stages
# variables of the dataframe:
# - club name
# - round of 32 group
# - position where the club finished in the group stages (winner = 1, runners up = 2)
# - which football association the club belongs to
group_2021_df = pd.DataFrame({
    'club': ['Manchester City', 'Paris Saint-Germain',
             'Liverpool', 'Atletico Madrid',
             'Ajax', 'Sporting CP Lisbon',
             'Real Madrid', 'Inter Milan',
             'Bayern Munich', 'Benfrica',
             'Manchester United', 'Villarreal',
             'Lille OSC', 'FC Salzburg',
             'Juventus', 'Chelsea'],

    'group': ['A', 'A', 'B', 'B', 'C', 'C', 'D', 'D',
              'E', 'E', 'F', 'F', 'G', 'G', 'H', 'H'],

    'finish': [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2],

    'country': ['Eng', 'Fra',
                'Eng', 'Esp',
                'Ned', 'Por',
                'Esp', 'Ita',
                'Ger', 'Por',
                'Eng', 'Esp',
                'Fra', 'Aut',
                'Ita', 'Eng']
})

# 2020 results of group stages
group_2020_df = pd.DataFrame({
    'club': ['Bayern Munich', 'Atletico Madrid',
             'Real Madrid', 'Monchengladbach',
             'Machester City', 'Porto',
             'Liverpool', 'Atalanta',
             'Chelsea', 'Sevilla',
             'Borussia Dortmund', 'Lazio',
             'Juventus', 'Barcelona',
             'Paris Saint-Germain', 'RB Leipzig'],

    'group': ['A', 'A', 'B', 'B', 'C', 'C', 'D', 'D',
              'E', 'E', 'F', 'F', 'G', 'G', 'H', 'H'],

    'finish': [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2],

    'country': ['Ger', 'Esp',
                'Esp', 'Ger',
                'Eng', 'Por',
                'Eng', 'Ita',
                'Eng', 'Esp',
                'Ger', 'Ita',
                'Ita', 'Esp',
                'Fra', 'Ger']
})

# eligibility check
# The round of 16 pairings are determined by means of a draw in accordance with the following principles:
# - Clubs from the same association cannot be drawn against each other.
# - Group winners must be drawn against runners-up from a different group.
# - The runners-up play the first leg at home.


def eligible_clubs(club_name, group_df):
    ok_clubs = []
    club_info = group_df[group_df['club'] == club_name]

    # select opposite of group winner/runner up
    # select from a different group
    # select from a different country
    group_subset = group_df.loc[(
        group_df['finish'] == (3 - club_info.finish.item()))]
    if group_subset.empty:
        raise ValueError(
            "No elgible clubs - either no more winners or runners up")
    else:
        group_subset = group_subset.loc[(
            group_df['country'] != club_info.country.item())]
        if group_subset.empty:
            raise ValueError(
                "No elgible clubs - all remaining clubs from same country")
        else:
            group_subset = group_subset.loc[(
                group_df['group'] != club_info.group.item())]
            if group_subset.empty:
                raise ValueError(
                    "No elgible clubs - all remaining clubs in same group")
            else:
                ok_clubs = group_subset['club']

                return ok_clubs


# example
eligible_clubs("Liverpool", group_2021_df)

# draw
# proceedure for draw:
# 1 - pick runner up at random
# 2 - select from eligible winners


def draw_clubs(last16_df):
    # initialise
    winners = last16_df[last16_df['finish'] == 1]['club']
    runners = last16_df[last16_df['finish'] == 2]['club']

    unchosen_clubs = last16_df.copy()
    matches = pd.DataFrame(columns=['match', 'winner', 'runner'])

    match_i = 1

    while not runners.empty:
        # 1 - pick runner up at random
        runner_club_idx = np.random.choice(runners.index)
        runner_club = runners.pop(runner_club_idx)

        # 2 - select from eligible winner
        try:
            ok_clubs = eligible_clubs(runner_club, unchosen_clubs)
        except ValueError as e:
            print(str(match_i - 1) + " matches drawn")
            raise ValueError(e)
        else:
            winner_club_idx = np.random.choice(ok_clubs.index)
            winner_club = winners.pop(winner_club_idx)

        # update unchosen clubs
        unchosen_clubs = unchosen_clubs.drop(
            labels=runner_club_idx,
            axis=0).drop(
            labels=winner_club_idx,
            axis=0)

        # record drawn teams
        matches.loc[match_i] = pd.Series({
            'match':  match_i,
            'winner': winner_club,
            'runner': runner_club})

        match_i += 1

    return matches


ro16_matches_2021 = draw_clubs(group_2021_df)
print(ro16_matches_2021)


# distribution of invalid draws
# around 1/5 draws are invalid, using the 2021 group stage standings
invalid_draws_n = 0
for i in range(0, 100):
    try:
        draw_i = draw_clubs(group_2021_df)
    except ValueError as e:
        print(e)
        invalid_draws_n += 1
print(str(invalid_draws_n/100) + " of draws were invalid using draw_clubs")

# enhanced draw mechanism to avoid no elgible clubs
# draw clubs that are likely to have no elgible clubs, these are:
# - from a country that have clubs in winner and runners up

# proceedure for draw:
# 1A - pick runner up at random from a country with clubs in winner and runner
# 1B - pick runner up at random
# 2 - select from eligible winners

# 1C - if the final two matches to draw have two clubs from the same group, there will be auto assign

last16_df = group_2020_df


def draw_clubs_country(last16_df):
    # initialise
    winners = last16_df[last16_df['finish'] == 1]['club']
    runners = last16_df[last16_df['finish'] == 2]['club']

    unchosen_clubs = last16_df.copy()
    matches = pd.DataFrame(columns=['match', 'winner', 'runner'])

    match_i = 1

    # select priority countries (have clubs in winner and runners up)
    priority_countries = last16_df.copy()
    priority_countries = priority_countries[['country', 'finish']].drop_duplicates(
    ).groupby(by=['country']).sum('finish').reset_index()
    priority_countries = priority_countries[priority_countries['finish'] == 3]

    # select clubs from priority countires
    priority_countries_pattern = '|'.join(priority_countries.country)

    priority_clubs = last16_df.copy()
    priority_clubs = priority_clubs[priority_clubs.country.str.contains(
        priority_countries_pattern)]

    priority_clubs_runners = priority_clubs[priority_clubs['finish'] == 2]['club']

    while not runners.empty:
        if (unchosen_clubs.shape[0] == 4) & (
                (unchosen_clubs.nunique().group < 4) | (unchosen_clubs.nunique().country < 4)):
            # 1C - assign matches if 2 teams remaining from the same group
            # 2nd last match
            # select club with group repeat or country repeat
            # if both group and country repeat and is winner and runners, then no solution using 4 clubs
            last4_df = unchosen_clubs.copy()

            last4_group_count = pd.DataFrame(
                unchosen_clubs.group.value_counts().reset_index())
            last4_group_count.columns = ['group', 'group_count']

            last4_country_count = pd.DataFrame(
                unchosen_clubs.country.value_counts().reset_index())
            last4_country_count.columns = ['country', 'country_count']

            last4_df = last4_df.reset_index().merge(
                last4_group_count, how="left").set_index('index')
            last4_df = last4_df.reset_index().merge(
                last4_country_count, how="left").set_index('index')

            runners_last = last4_df.loc[(last4_df['finish'] == 2) &
                                        ((last4_df['group_count'] == 2) |
                                         (last4_df['country_count'] == 2))]
            if runners_last.empty:
                runners_last = last4_df.loc[(last4_df['finish'] == 2)]

            runner_club_idx = np.random.choice(runners_last.index)
            runner_club = runners.pop(runner_club_idx)

        elif not priority_clubs_runners.empty:
            # 1A - pick runner up at random from a country with clubs in winner and runner
            runner_club_idx = np.random.choice(priority_clubs_runners.index)
            runner_club = runners.pop(runner_club_idx)

        else:
            # 1B - pick runner up at random
            runner_club_idx = np.random.choice(runners.index)
            runner_club = runners.pop(runner_club_idx)

        # 2 - select from eligible winner
        try:
            ok_clubs = eligible_clubs(runner_club, unchosen_clubs)
        except ValueError as e:
            print(str(match_i - 1) + " matches drawn")
            raise ValueError(e)
        else:
            winner_club_idx = np.random.choice(ok_clubs.index)
            winner_club = winners.pop(winner_club_idx)

        # update unchosen clubs
        unchosen_clubs = unchosen_clubs.drop(
            labels=runner_club_idx,
            axis=0).drop(
            labels=winner_club_idx,
            axis=0)

        try:
            priority_clubs_runners.pop(runner_club_idx)
        except KeyError:
            pass

        # record drawn teams
        matches.loc[match_i] = pd.Series({
            'match':  match_i,
            'winner': winner_club,
            'runner': runner_club})

        match_i += 1

    return matches


ro16_matches_2021 = draw_clubs_country(group_2021_df)
print(ro16_matches_2021)

# updated distribution of invalid draws
# no draws are invalid, using the 2021 group stage standings and enhanced draw mechanism
# 5% draws are invalid, using the 2020 group stage standings
invalid_draws_enhanced_n = 0
for i in range(0, 100):
    try:
        draw_i = draw_clubs_country(group_2020_df)
    except ValueError as e:
        print(e)
        invalid_draws_enhanced_n += 1
print(str(invalid_draws_enhanced_n/100) +
      " of draws were invalid using draw_clubs_country")


# alternate draw between winners and runners up (as performed in 2020 draw)
# but will first prioritise countries with winners and runners up
def draw_clubs_country_alt(last16_df):
    # initialise
    winners = last16_df[last16_df['finish'] == 1]['club']
    runners = last16_df[last16_df['finish'] == 2]['club']

    unchosen_clubs = last16_df.copy()
    matches = pd.DataFrame(columns=['match', 'winner', 'runner'])

    match_i = 1

    # select priority countries (have clubs in winner and runners up)
    priority_countries = last16_df.copy()
    priority_countries = priority_countries[['country', 'finish']].drop_duplicates(
    ).groupby(by=['country']).sum('finish').reset_index()
    priority_countries = priority_countries[priority_countries['finish'] == 3]

    # select clubs from priority countires
    priority_countries_pattern = '|'.join(priority_countries.country)

    priority_clubs = last16_df.copy()
    priority_clubs = priority_clubs[priority_clubs.country.str.contains(
        priority_countries_pattern)]

    priority_clubs_winners = priority_clubs[priority_clubs['finish'] == 1]['club']
    priority_clubs_runners = priority_clubs[priority_clubs['finish'] == 2]['club']

    while not unchosen_clubs.empty:
        if (unchosen_clubs.shape[0] == 4) & (
                (unchosen_clubs.nunique().group < 4) | (unchosen_clubs.nunique().country < 4)):
            # 1C - assign matches if 2 teams remaining from the same group
            # 2nd last match
            # select club with group repeat or country repeat
            # if both group and country repeat and is winner and runners, then no solution using 4 clubs
            last4_df = unchosen_clubs.copy()

            last4_group_count = pd.DataFrame(
                unchosen_clubs.group.value_counts().reset_index())
            last4_group_count.columns = ['group', 'group_count']

            last4_country_count = pd.DataFrame(
                unchosen_clubs.country.value_counts().reset_index())
            last4_country_count.columns = ['country', 'country_count']

            last4_df = last4_df.reset_index().merge(
                last4_group_count, how="left").set_index('index')
            last4_df = last4_df.reset_index().merge(
                last4_country_count, how="left").set_index('index')

            if match_i % 2 == 1:
                runners_last = last4_df.loc[(last4_df['finish'] == 2) &
                                            ((last4_df['group_count'] == 2) |
                                             (last4_df['country_count'] == 2))]
                if runners_last.empty:
                    runners_last = last4_df.loc[(last4_df['finish'] == 2)]

                runner_club_idx = np.random.choice(runners_last.index)
                runner_club = runners.pop(runner_club_idx)
            else:
                winners_last = last4_df.loc[(last4_df['finish'] == 1) &
                                            ((last4_df['group_count'] == 2) |
                                             (last4_df['country_count'] == 2))]
                if winners_last.empty:
                    winners_last = last4_df.loc[(last4_df['finish'] == 1)]

                winner_club_idx = np.random.choice(winners_last.index)
                winner_club = winners.pop(runner_club_idx)

        elif (match_i % 2 == 1) & (not priority_clubs_runners.empty):
            # 1A - pick winner/runner up at random from a country with clubs in winner and runner
            runner_club_idx = np.random.choice(priority_clubs_runners.index)
            runner_club = runners.pop(runner_club_idx)

        elif (match_i % 2 == 0) & (not priority_clubs_winners.empty):
            # 1A - pick winner/runner up at random from a country with clubs in winner and runner
            winner_club_idx = np.random.choice(priority_clubs_winners.index)
            winner_club = winners.pop(winner_club_idx)

        else:
            # 1B - pick winner/runner up at random
            if match_i % 2 == 1:
                runner_club_idx = np.random.choice(runners.index)
                runner_club = runners.pop(runner_club_idx)
            else:
                winner_club_idx = np.random.choice(winners.index)
                winner_club = winners.pop(winner_club_idx)

        # 2 - select from eligible winner/runner up
        try:
            if match_i % 2 == 1:
                ok_clubs = eligible_clubs(runner_club, unchosen_clubs)
            else:
                ok_clubs = eligible_clubs(winner_club, unchosen_clubs)
        except ValueError as e:
            print(str(match_i - 1) + " matches drawn")
            raise ValueError(e)
        else:
            if match_i % 2 == 1:
                winner_club_idx = np.random.choice(ok_clubs.index)
                winner_club = winners.pop(winner_club_idx)
            else:
                runner_club_idx = np.random.choice(ok_clubs.index)
                runner_club = runners.pop(runner_club_idx)

        # update unchosen clubs
        unchosen_clubs = unchosen_clubs.drop(
            labels=runner_club_idx,
            axis=0).drop(
            labels=winner_club_idx,
            axis=0)

        try:
            priority_clubs = priority_clubs.drop(
                labels=winner_club_idx,
                axis=0)
        except KeyError:
            pass

        try:
            priority_clubs = priority_clubs.drop(
                labels=runner_club_idx,
                axis=0)
        except KeyError:
            pass

        priority_clubs_winners = priority_clubs[priority_clubs['finish'] == 1]['club']
        priority_clubs_runners = priority_clubs[priority_clubs['finish'] == 2]['club']

        # record drawn teams
        matches.loc[match_i] = pd.Series({
            'match':  match_i,
            'winner': winner_club,
            'runner': runner_club})

        match_i += 1

    return matches


# updated distribution of invalid draws
# some invalid draws remain
invalid_draws_enhanced_alt_n = 0
for i in range(0, 100):
    try:
        draw_i = draw_clubs_country_alt(group_2021_df)
    except ValueError as e:
        print(e)
        invalid_draws_enhanced_alt_n += 1
print(str(invalid_draws_enhanced_alt_n/100) +
      " of draws were invalid using draw_clubs_country_alt")


# enhanced draw mechanism to avoid no elgible clubs
# draw clubs in batches based on number of eligible clubs remaining

# proceedure for draw:
# 0 - order runner up by number of eligible teams
# 1 - pick runner up at random (if same number of eligble teams)
# 2 - select from eligible winners
# 3 - randomise match numbers

# 1C - if the final two matches to draw have two clubs from the same group, there will be auto assign

def draw_clubs_order(last16_df):
    # initialise
    winners = last16_df[last16_df['finish'] == 1]['club']
    runners = last16_df[last16_df['finish'] == 2]['club']

    unchosen_clubs = last16_df.copy()
    matches = pd.DataFrame(columns=['match', 'winner', 'runner'])

    match_i = 1

    # 0 - order runner up by "difficulty" (number of eligible teams)
    unchosen_clubs['eli_clubs'] = 0
    for r in runners:
        unchosen_clubs.loc[unchosen_clubs['club'] == r, 'eli_clubs'] = eligible_clubs(
            r, unchosen_clubs).shape[0]

    while not runners.empty:
        if (unchosen_clubs.shape[0] == 4) & (
                (unchosen_clubs.nunique().group < 4) | (unchosen_clubs.nunique().country < 4)):
            # 1C - assign matches if 2 teams remaining from the same group
            # 2nd last match
            # select club with group repeat or country repeat
            # if both group and country repeat and is winner and runners, then no solution using 4 clubs
            last4_df = unchosen_clubs.copy()

            last4_group_count = pd.DataFrame(
                unchosen_clubs.group.value_counts().reset_index())
            last4_group_count.columns = ['group', 'group_count']

            last4_country_count = pd.DataFrame(
                unchosen_clubs.country.value_counts().reset_index())
            last4_country_count.columns = ['country', 'country_count']

            last4_df = last4_df.reset_index().merge(
                last4_group_count, how="left").set_index('index')
            last4_df = last4_df.reset_index().merge(
                last4_country_count, how="left").set_index('index')

            runners_last = last4_df.loc[(last4_df['finish'] == 2) &
                                        ((last4_df['group_count'] == 2) |
                                         (last4_df['country_count'] == 2))]
            if runners_last.empty:
                runners_last = last4_df.loc[(last4_df['finish'] == 2)]

            runner_club_idx = np.random.choice(runners_last.index)
            runner_club = runners.pop(runner_club_idx)

        else:
            # 1 - pick runner up at random (if same number of eligble teams)
            eli_club_i = sorted(set(unchosen_clubs.eli_clubs))[1]
            runners_draw_df = unchosen_clubs.loc[unchosen_clubs['eli_clubs'] == eli_club_i]

            runner_club_idx = np.random.choice(runners_draw_df.index)
            runner_club = runners.pop(runner_club_idx)

        # 2 - select from eligible winner
        try:
            ok_clubs = eligible_clubs(runner_club, unchosen_clubs)
        except ValueError as e:
            raise ValueError(e)
        else:
            winner_club_idx = np.random.choice(ok_clubs.index)
            winner_club = winners.pop(winner_club_idx)

        # update unchosen clubs
        unchosen_clubs = unchosen_clubs.drop(
            labels=runner_club_idx,
            axis=0).drop(
            labels=winner_club_idx,
            axis=0)

        for r in runners:
            unchosen_clubs.loc[unchosen_clubs['club'] == r, 'eli_clubs'] = eligible_clubs(
                r, unchosen_clubs).shape[0]

        # record drawn teams
        matches.loc[match_i] = pd.Series({
            'match':  match_i,
            'winner': winner_club,
            'runner': runner_club})

        match_i += 1

    # 3 - randomise match number
    matches = matches.sample(frac=1).reset_index(drop=True)
    matches.match = range(1, matches.shape[0] + 1)

    return matches


ro16_matches_2021 = draw_clubs_order(group_2021_df)
print(ro16_matches_2021)

# updated distribution of invalid draws
# no draws are invalid, using the 2021 group stage standings and enhanced ordered draw mechanism
# no draws are invalid, using the 2020 group stage standings and enhanced ordered draw mechanism
invalid_draws_order_n = 0
for i in range(0, 100):
    try:
        draw_i = draw_clubs_order(group_2021_df)
    except ValueError as e:
        print(e)
        print('=================')
        print(i)
        invalid_draws_order_n += 1
print(str(invalid_draws_order_n/100) +
      " of draws were invalid using draw_clubs_order")
