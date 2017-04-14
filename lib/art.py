# -*- coding: utf-8 -*-
from lib import tools


__sport = {
    'SOCCER': {
        'icon': 'futbol.png',
        'fanart': 'futbol_art.jpg'
    },
    'BASKETBALL': {
        'icon': 'basket.png',
        'fanart': 'basket_art.jpg'
    },
    'FORMULA 1': {
        'icon': 'f1.png',
        'fanart': 'f1_art.jpg'
    },
    'MOTOGP': {
        'icon': 'motogp.png',
        'fanart': 'motogp_art.jpg'
    },
    'TENNIS': {
        'icon': 'tenis.png',
        'fanart': 'tenis_art.jpg'
    },
    'MMA': {
        'icon': 'mma.png',
        'fanart': 'mma_art.jpg'
    },
    'CYCLING': {
        'icon': 'ciclismo.png',
        'fanart': 'ciclismo_art.jpg'
    },
    'FOOTBALL': {
        'icon': 'rugby.png',
        'fanart': 'rugby_art.jpg'
    },
    'BASEBALL': {
        'icon': 'baseball.png',
        'fanart': 'baseball_art.jpg'
    },
    'VOLLEYBALL': {
        'icon': 'voley.png',
        'fanart': 'voley_art.jpg'
    },
    'GOLF': {
        'icon': 'golf.png',
        'fanart': 'golf_art.jpg'
    },
    'HOCKEY': {
        'icon': 'hockey.png',
        'fanart': 'hockey_art.jpg'
    },
    'RUGBY': {
        'icon': 'rugby.png',
        'fanart': 'rugby_art.jpg'
    },
    'BOXING': {
        'icon': 'boxeo.png',
        'fanart': 'boxeo_art.jpg'
    }
}

__competition = {
    'LA LIGA': 'liga_es_1.png',
    'SPANISH LA LIGA': 'liga_es_1.png',
    'SPANISH LA LIGA 2': 'liga_es_2.png',
    'SPANISH PRIMERA DIVISION': 'liga_es_1.png',
    'SPANISH SEGUNDA DIVISION': 'liga_es_2.png',
    'BUNDESLIGA': 'liga_de_1.png',
    'GERMAN BUNDESLIGA': 'liga_de_1.png',
    'ITALIA CUP': 'copa_italia.png',
    'PREMIER LEAGUE': 'liga_en.png',
    'ENGLISH PREMIER LEAGUE': 'liga_en.png',
    'PORTUGAL CUP': 'liga_po.png',
    'USA NBA': 'nba.png',
    'USA NBA PLAYOFFS': 'nba_playoffs.png',
    'USA MLS': 'liga_usa_mls.png',
    'MLS': 'liga_usa_mls.png',
    'LIGA MX': 'liga_mx.png',
    'MEXICO LIGA MX': 'liga_mx.png',
    'MEXICO COPA MX': 'copa_mx.png',
    'COPA LIBERTADORES': 'copa_libertadores.png',
    'COPA SUDAMERICANA': 'copa_sudamerica.png',
    'CONCACAF CHAMPIONS LEAGUE': 'concaf_champions.jpg',
    'URUGUAY LEAGUE': 'liga_ur.png',
    'URUGUAY PRIMERA': 'liga_ur.png',
    'COLOMBIA PRIMERA': 'copa_colombia.png',
    'COLOMBIA COPA': 'copa_colombia.png',
    'ARGENTINA PRIMERA': 'liga_ar.png',
    'PRIMERA DIVISION': 'liga_ar.png',
    'LIGUE 1': 'liga_fr.png',
    'FRENCH LIGUE 1': 'liga_fr.png',
    'FRENCH CUP': 'copa_francia.png',
    'CHILE LEAGUE': 'liga_ch.png',
    'ITALY SERIE A': 'liga_it_serie_a.png',
    'ITALIAN SERIE A': 'liga_it_serie_a.png',
    'SERIE A': 'liga_it_serie_a.png',
    'PORTUGAL A LIGA': 'liga_po.png',
    'PRIMEIRA LIGA': 'liga_po.png',
    'SPANISH ACB': 'liga_acb.png',
    'EUROLEAGUE': 'euroliga.png',
    'WBO WORLD TITLE': 'wbo.png',
    'UEFA CHAMPIONS LEAGUE': 'champions_league.png',
    'UEFA EUROPA LEAGUE': 'europa_league.png',
    'ATP WORLD TOUR': 'atp_world_tour.png',
    'A-LEAGUE': 'liga_au.png',
    'CHAMPIONSHIP': 'liga_efl.png',
    'EREDIVISIE': 'liga_ho.png',
    'SCOTTISH PREMIERSHIP': 'liga_esc.png',
    'RUSSIAN PREMIER LEAGUE': 'liga_ru.png',
    'J1 LEAGUE': 'liga_j1.png',
    'PAULISTA A1': 'liga_br_sao.png'
}

__genre = {
    'Música': {
        'icon': 'musica.png',
        'fanart': 'musica_art.jpg'
    },
    'Educativo': {
        'icon': 'educativo.png',
        'fanart': 'educativo_art.jpg'
    },
    'Adultos': {
        'icon': 'adultos.png',
        'fanart': 'adultos_art.jpg'
    },
    'Películas': {
        'icon': 'peliculas.png',
        'fanart': 'ttv_art.jpg'
    },
    'Deportes': {
        'icon': 'sports.png',
        'fanart': 'sports_art.jpg'
    }
}


def get_sport_art(sport, path):
    """

    :param sport: 
    :param path: 
    :return: 
    """
    art = __sport.get(tools.str_sanitize(sport).upper(), {
        'icon': 'sports.png',
        'fanart': 'sports_art.jpg'
    })

    return {
        'icon': tools.build_path(path, art['icon']),
        'fanart': tools.build_path(path, art['fanart'])
    }


def get_competition_icon(competition, path, default=None):
    """

    :param competition: 
    :param path: 
    :param default: 
    :return: 
    """
    icon = __competition.get(tools.str_sanitize(competition).upper(), default)

    if icon:
        icon = tools.build_path(path, icon)

    return icon


def get_genre_art(genre, path):
    """
    Get a dict containing the icon and fanart URLs for a given category

    :return: The dict containing icon and fanart for a given category
    :rtype: dict
    """
    art = __genre.get(genre, {
        'icon': 'sports.png',
        'fanart': 'sports_art.jpg'
    })

    return {
        'icon': tools.build_path(path, art['icon']),
        'fanart': tools.build_path(path, art['fanart'])
    }


def get_channel_art(channel_name, path):
    if 'arenavision' in channel_name.lower():
        return tools.build_path(path, 'arenavision.jpg')

    elif 'tsn' in channel_name.lower():
        return tools.build_path(path, 'tsn.png')

    elif 'match' in channel_name.lower():
        return tools.build_path(path, 'match.png')

    elif 'viasat' in channel_name.lower():
        return tools.build_path(path, 'viasat.png')

    elif ' UA' in channel_name:
        return tools.build_path(path, 'ua.png')

    else:
        return tools.build_path(path, 'acestream.png')
