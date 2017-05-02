# -*- coding: utf-8 -*-

__es = {
    # Categorías/Géneros de TorrentTV
    'genre': {
        u'узыка': 'Música',
        u'ознавательные': 'Educativo',
        u'ротика': 'Adultos',
        u'ильмы': 'Películas',
        u'порт': 'Deportes'
    },
    # Deportes
    'SOCCER': 'Fútbol',
    'BASKETBALL': 'Baloncesto',
    'FORMULA 1': 'Formula 1',
    'MOTOGP': 'Moto GP',
    'MOTO GP': 'Moto GP',
    'TENNIS': 'Tenis',
    'MMA': 'Lucha',
    'CYCLING': 'Ciclismo',
    'FOOTBALL': 'Football americano',
    'BASEBALL': 'Beisbol',
    'VOLLEYBALL': 'Voleybol',
    'GOLF': 'Golf',
    'HOCKEY': 'Hockey',
    'RUGBY': 'Rugby',
    'BOXING': 'Boxeo',
    # Competiciones
    'UEFA CHAMPIONS LEAGUE': 'UEFA Champions League',
    'UEFA WOMEN CHAMPIONS LEAGUE': 'UEFA Champions League Fenemina',
    'UEFA EUROPA LEAGUE': 'UEFA Europa League',
    'UEFA EURO U-17': 'UEFA Eurocopa Sub-17',
    'UEFA YOUTH LEAGUE': 'UEFA Youth League',
    'URUGUAY LEAGUE': 'Liga Uruguaya',
    'URUGUAY PRIMERA': 'Liga Uruguaya',
    'COPA SUDAMERICANA': 'Copa Sudamericana',
    'COPA LIBERTADORES': 'Copa Libertadores',
    'BRAZIL CUP': 'Copa de Brasil',
    'COLOMBIA PRIMERA': 'Liga Colombiana',
    'COLOMBIA COPA': 'Copa de Colombia',
    'ARGENTINA PRIMERA': 'Liga Argentina',
    'MEXICO COPA MX': 'Copa de Mexico',
    'MEXICO LIGA MX': 'Liga Mexicana',
    'SPANISH LA LIGA': 'La Liga',
    'SPANISH LA LIGA 2': 'La Liga 123',
    'EUROLEAGUE': 'Euroliga',
    'PORTUGAL A LIGA': 'Liga Portuguesa',
    'CHILE LEAGUE': 'Liga Chilena',
    'DAVIS CUP': 'Davis CUP',
    'FRENCH LIGUE 1': 'Liga Francesa',
    'FRENCH LEAGUE': 'Liga Francesa',
    'ITALY SERIE A': 'Liga Italiana',
    'PREMIER LEAGUE': 'Liga Inglesa',
    'BUNDESLIGA': 'Liga Alemana',
    'USA MLS': 'Liga de USA',
    'SPANISH ACB': 'Liga ACB',
    'USA NBA': 'NBA',
    'USA NBA PLAYOFF': 'Playoffs de la NBA',
    'USA NBA PLAYOFFS': 'Playoffs de la NBA',
    'WBO WORLD TITLE': 'Titulo Mundial WBO',
    'ATP WORLD TOUR': 'ATP World Tour',
    'ATPWORLD TOUR': 'ATP World Tour',
    'SPANISH PRIMERA DIVISION': 'La Liga',
    'SPANISH SEGUNDA DIVISION': 'La Liga 123',
    'ENGLISH PREMIER LEAGUE': 'Liga Inglesa',
    'FA CUP': 'Copa Inglesa',
    'ENGLISH FA CUP': 'Copa Inglesa',
    'BELGIAN LEAGUE': 'Liga Belga',
    'KNVB BEKER': 'Copa Holandesa',
    'SUPER LIG': 'Liga Turka',
    'AFC CUP': 'Copa AFC',
    'AFC CHAMPIONS LEAGUE': 'AFC Champions League',
    'ITALIAN SERIE A': 'Liga Italiana',
    'ITALY SERIA A': 'Liga Italiana',
    'GERMAN BUNDESLIGA': 'Liga Alemana',
    'A-LEAGUE': 'Liga Australiana',
    'CHAMPIONSHIP': 'Campeonato EFL',
    'PRIMEIRA LIGA': 'Liga Portuguesa',
    'EREDIVISIE': 'Liga Holandesa',
    'SCOTTISH PREMIERSHIP': 'Liga Escocesa',
    'LIGUE 1': 'Liga Francesa',
    'MLS': 'Liga de USA',
    'RUSSIAN PREMIER LEAGUE': 'Liga Rusa',
    'SERIE A': 'Liga Italiana',
    'LA LIGA': 'La Liga',
    'LIGA MX': 'Liga Mexicana',
    'PRIMERA DIVISION': 'Liga Argentina',
    'J1 LEAGUE': 'Liga Japonesa',
    'PAULISTA A1': 'Liga de Sao Paulo'
}


def translate(name, lang='es', default_none=False):
    if lang == 'en':
        return name
    elif lang == 'es':
        translation = __es.get(name.upper(), None)
        if translation:
            return translation
        elif default_none:
            return None
    return name


def genre(name, lang='es', default_none=True):
    if lang == 'ru':
        return name
    elif lang == 'es':
        translation = __es['genre'].get(name, None)
        if translation:
            return translation
        elif default_none:
            return None
    return name
