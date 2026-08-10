from django.db import models


class DrinkType(models.TextChoices):
    COFFEE = "coffee", "커피"
    TEA = "tea", "차"
    SODA = "soda", "탄산"
    ENERGY = "energy", "에너지드링크"
    OTHER = "other", "기타"


class Brand(models.TextChoices):
    # 커피, 차
    STARBUCKS = "starbucks", "스타벅스"
    EDIYA = "ediya", "이디야커피"
    MEGA = "mega", "메가MGC커피"
    COMPOSE = "compose", "컴포즈커피"
    GONGCHA = "gongcha", "공차"
    BAIKDABANG = "baikdabang", "빽다방"
    MAMMOTH = "mammoth", "매머드커피"
    
    # 에너지드링크
    MONSTER = "monster", "몬스터"
    HOTSIX = "hotsix", "핫식스"
    REDBULL = "redbull", "레드불"
    
    # 탄산음료
    PEPSI = "pepsi", "펩시"
    COCACOLA = "cocacola", "코카콜라"
    
    CUSTOM = "custom", "직접 입력"