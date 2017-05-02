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
    'MOTO GP': {
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
    'FA CUP': 'copa_fa.png',
    'ENGLISH FA CUP': 'copa_fa.png',
    'ENGLISH PREMIER LEAGUE': 'liga_en.png',
    'PORTUGAL CUP': 'liga_po.png',
    'BRAZIL CUP': 'copa_br.png',
    'USA NBA': 'nba.png',
    'USA NBA PLAYOFF': 'nba_playoffs.png',
    'USA NBA PLAYOFFS': 'nba_playoffs.png',
    'USA MLS': 'liga_usa_mls.png',
    'MLS': 'liga_usa_mls.png',
    'LIGA MX': 'liga_mx.png',
    'MEXICO LIGA MX': 'liga_mx.png',
    'MEXICO COPA MX': 'copa_mx.png',
    'AFC CUP': 'copa_afc.png',
    'AFC CHAMPIONS LEAGUE': 'afc_champions_league.png',
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
    'FRENCH LEAGUE': 'liga_fr.png',
    'FRENCH CUP': 'copa_francia.png',
    'CHILE LEAGUE': 'liga_ch.png',
    'ITALY SERIE A': 'liga_it_serie_a.png',
    'ITALY SERIA A': 'liga_it_serie_a.png',
    'ITALIAN SERIE A': 'liga_it_serie_a.png',
    'SERIE A': 'liga_it_serie_a.png',
    'PORTUGAL A LIGA': 'liga_po.png',
    'PRIMEIRA LIGA': 'liga_po.png',
    'BELGIAN LEAGUE': 'liga_be.png',
    'KNVB BEKER': 'copa_ho.png',
    'SUPER LIG': 'liga_tu.png',
    'SPANISH ACB': 'liga_acb.png',
    'EUROLEAGUE': 'euroliga.png',
    'WBO WORLD TITLE': 'wbo.png',
    'UEFA CHAMPIONS LEAGUE': 'champions_league.png',
    'UEFA WOMEN CHAMPIONS LEAGUE': 'uefa_women_cl.png',
    'UEFA EUROPA LEAGUE': 'europa_league.png',
    'UEFA EURO U-17': 'uefa_euro_u17.png',
    'UEFA YOUTH LEAGUE': 'liga_uefa_youth.png',
    'ATP WORLD TOUR': 'atp_world_tour.png',
    'ATPWORLD TOUR': 'atp_world_tour.png',
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


def get_channel_icon(channel_name, path):
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

        # 'Sexta', '24', 'Clan', 'Teledeporte', 'Neox', 'Nova',
        # 'Atres', 'Mega', 'FDF', 'Energy', 'Be Mad', 'Divinity', 'Boing', 'Gol', 'MAX', '13tv', 'Intereconom',
        # 'Disney Channel', 'TEN', 'Kiss', 'Real Madrid', 'Paramount', 'Telemadrid', 'Otra', 'TV3', '33', 'sport 3',
        # 'TB 1', 'TB 2', 'TB 3', 'TB 4', 'TVG', 'Canal Sur', 'Andaluc', 'Mancha', 'Arag', 'TPA', 'Extremadura',
        # 'Estrenos', 'Series', '#0', 'tbol', 'beIN LaLiga', 'beIN Sport', 'AXN', 'Life', 'FOX', 'TNT', 'Nickelodeon',
        # 'Calle 13', 'Sy', 'Historia', 'Geographic', 'Odis', 'Discovery', 'COSMO', 'Decasa', 'Cocina', 'Viajar',
        # 'Hollywood', 'Comedy', 'Non Stop', 'Eurosport', 'MTV', 'TCM', 'AMC', 'Formula 1', 'MotoGP', 'Barca'


def get_epg_channel_logo(channel_name, path):

    if 'formula' in channel_name:
        return tools.build_path(path, 'mf1.png')

    elif 'la1' in channel_name:
        return tools.build_path(path, 'la1.png')

    elif 'la2' in channel_name:
        return tools.build_path(path, 'la2.png')

    elif 'antena3' in channel_name:
        return tools.build_path(path, 'antena3.png')

    elif 'cuatro' in channel_name:
        return tools.build_path(path, 'cuatro.png')

    elif ('telecinco' or 'tele5') in channel_name:
        return tools.build_path(path, 'telecinco.png')

    elif 'sexta' in channel_name:
        return tools.build_path(path, 'lasexta.png')

    elif 'realmadrid' in channel_name:
        return tools.build_path(path, 'realmadridtv.png')

    elif 'teledeporte' in channel_name:
        return tools.build_path(path, 'teledeporte.png')

    elif '13tv' in channel_name:
        return tools.build_path(path, '13tv.png')

    else:
        return tools.build_path(path, 'movistar.png')
