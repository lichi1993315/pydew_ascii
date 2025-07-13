import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

@dataclass
class Fish:
    """
    鱼类数据结构
    """
    name: str           # 鱼的名称
    rarity: str         # 稀有度 (common, uncommon, rare, epic, legendary)
    min_length: int     # 最小长度(厘米)
    max_length: int     # 最大长度(厘米)
    base_price: int     # 基础价格
    color: Tuple[int, int, int]  # RGB颜色
    ascii_char: str     # ASCII字符表示
    catch_rate: float   # 捕获概率(0-1)
    description: str    # 详细描述

@dataclass
class CatCatch:
    """
    钓到猫咪的数据结构
    """
    name: str           # 猫咪名称
    personality: str    # 性格描述
    rarity: str         # 稀有度
    color: Tuple[int, int, int]  # RGB颜色
    ascii_char: str     # ASCII字符表示
    catch_rate: float   # 捕获概率

@dataclass
class TrashCatch:
    """
    钓到垃圾物品的数据结构
    """
    name: str           # 物品名称
    category: str       # 分类 (trash, treasure, natural)
    rarity: str         # 稀有度
    value: int          # 价值（可能是负数）
    color: Tuple[int, int, int]  # RGB颜色
    ascii_char: str     # ASCII字符表示
    catch_rate: float   # 捕获概率
    description: str    # 详细描述

class FishSystem:
    """
    鱼类系统管理器（包含钓到猫咪和垃圾物品的功能）
    """
    
    def __init__(self):
        # 定义所有鱼类
        self.fish_types = {
            # 普通鱼类 - 白色
            'minnow': Fish(
                name='小鱼',
                rarity='common',
                min_length=5,
                max_length=12,
                base_price=3,
                color=(255, 255, 255),
                ascii_char='><>',
                catch_rate=0.4,
                description='体型娇小的淡水鱼，游泳速度快，是最常见的钓鱼目标。肉质鲜美，适合做汤。'
            ),
            'carp': Fish(
                name='鲤鱼',
                rarity='common',
                min_length=15,
                max_length=30,
                base_price=8,
                color=(255, 255, 255),
                ascii_char='><)))',
                catch_rate=0.25,
                description='常见的淡水鱼，体型较大，肉质肥美。在很多文化中都是吉祥的象征。'
            ),
            
            # 不常见鱼类 - 绿色
            'bass': Fish(
                name='鲈鱼',
                rarity='uncommon',
                min_length=20,
                max_length=45,
                base_price=15,
                color=(0, 255, 0),
                ascii_char='><))))',
                catch_rate=0.15,
                description='肉食性鱼类，攻击性强，喜欢捕食小鱼。肉质紧实，味道鲜美，是钓鱼爱好者的热门目标。'
            ),
            'trout': Fish(
                name='鳟鱼',
                rarity='uncommon',
                min_length=18,
                max_length=40,
                base_price=18,
                color=(0, 255, 0),
                ascii_char='><(((',
                catch_rate=0.12,
                description='生活在清澈冷水中的鱼类，对水质要求很高。肉质细嫩，营养丰富，是高档食材。'
            ),
            
            # 稀有鱼类 - 蓝色
            'salmon': Fish(
                name='三文鱼',
                rarity='rare',
                min_length=30,
                max_length=60,
                base_price=35,
                color=(0, 150, 255),
                ascii_char='><))))*',
                catch_rate=0.06,
                description='回游性鱼类，拥有强烈的生存本能。肉质鲜美，富含营养，是世界闻名的美食。'
            ),
            'pike': Fish(
                name='梭鱼',
                rarity='rare',
                min_length=35,
                max_length=70,
                base_price=40,
                color=(0, 150, 255),
                ascii_char='><---)',
                catch_rate=0.05,
                description='淡水中的顶级掠食者，身体修长，牙齿锋利。性情凶猛，是钓鱼的挑战性目标。'
            ),
            
            # 新增稀有鱼类
            'blue_gourami': Fish(
                name='蓝曼龙鱼',
                rarity='rare',
                min_length=8,
                max_length=15,
                base_price=25,
                color=(0, 100, 255),
                ascii_char='🐟',
                catch_rate=0.08,
                description='美丽的热带观赏鱼，体色鲜艳，性情温和。在野外环境中较为罕见，具有很高的观赏价值。'
            ),
            'tropical_fish': Fish(
                name='热带鱼',
                rarity='uncommon',
                min_length=6,
                max_length=20,
                base_price=20,
                color=(255, 100, 0),
                ascii_char='🐠',
                catch_rate=0.10,
                description='色彩绚丽的热带鱼类，栖息在温暖的水域中。每一条都有独特的花纹和颜色。'
            ),
            'pufferfish': Fish(
                name='河豚',
                rarity='epic',
                min_length=10,
                max_length=25,
                base_price=100,
                color=(255, 255, 0),
                ascii_char='🐡',
                catch_rate=0.03,
                description='有毒的鱼类，受到威胁时会膨胀成球状。虽然危险，但在某些地方是珍贵的食材。'
            ),
            'shark': Fish(
                name='小鲨鱼',
                rarity='epic',
                min_length=40,
                max_length=80,
                base_price=150,
                color=(100, 100, 100),
                ascii_char='🦈',
                catch_rate=0.015,
                description='海洋中的王者，即使是幼体也展现出强大的力量。钓到它需要极大的勇气和技巧。'
            ),
            'octopus': Fish(
                name='章鱼',
                rarity='epic',
                min_length=20,
                max_length=50,
                base_price=120,
                color=(160, 0, 160),
                ascii_char='🐙',
                catch_rate=0.025,
                description='聪明的海洋生物，拥有八条触手和惊人的智力。能够改变体色，是海洋中的伪装大师。'
            ),
            'squid': Fish(
                name='鱿鱼',
                rarity='rare',
                min_length=15,
                max_length=40,
                base_price=45,
                color=(255, 200, 200),
                ascii_char='🦑',
                catch_rate=0.07,
                description='海洋中的快速游泳者，拥有十条触手。遇到危险时会喷出墨汁逃跑。'
            ),
            'shrimp': Fish(
                name='虾',
                rarity='common',
                min_length=3,
                max_length=8,
                base_price=5,
                color=(255, 150, 150),
                ascii_char='🦐',
                catch_rate=0.30,
                description='小巧的甲壳动物，味道鲜美，营养丰富。在水中快速游动，是很多鱼类的食物。'
            ),
            
            # 史诗鱼类 - 紫色
            'swordfish': Fish(
                name='剑鱼',
                rarity='epic',
                min_length=50,
                max_length=100,
                base_price=80,
                color=(160, 0, 255),
                ascii_char='><=====>',
                catch_rate=0.02,
                description='拥有剑状长嘴的大型海鱼，游速极快。是深海中的优雅猎手，钓到它是钓鱼者的荣耀。'
            ),
            'dolphin': Fish(
                name='海豚',
                rarity='legendary',
                min_length=100,
                max_length=200,
                base_price=500,
                color=(100, 150, 255),
                ascii_char='🐬',
                catch_rate=0.005,
                description='聪明友好的海洋哺乳动物，拥有高度发达的智力。遇到它是极其罕见的幸运事件。'
            ),
            'whale': Fish(
                name='小鲸鱼',
                rarity='legendary',
                min_length=200,
                max_length=400,
                base_price=1000,
                color=(0, 0, 200),
                ascii_char='🐋',
                catch_rate=0.002,
                description='海洋中的巨无霸，即使是幼体也拥有惊人的体型。能够钓到它几乎是不可能的奇迹。'
            ),
            'seal': Fish(
                name='海豹',
                rarity='epic',
                min_length=80,
                max_length=150,
                base_price=200,
                color=(100, 100, 50),
                ascii_char='🦭',
                catch_rate=0.01,
                description='可爱的海洋哺乳动物，善于游泳和潜水。性情温和，遇到人类通常很友好。'
            ),
            'otter': Fish(
                name='水獭',
                rarity='rare',
                min_length=30,
                max_length=60,
                base_price=80,
                color=(139, 69, 19),
                ascii_char='🦦',
                catch_rate=0.04,
                description='生活在水边的可爱动物，善于游泳和捕鱼。毛茸茸的外表下隐藏着敏捷的身手。'
            ),
            
            # 新增水生生物
            'jellyfish': Fish(
                name='水母',
                rarity='uncommon',
                min_length=10,
                max_length=30,
                base_price=22,
                color=(200, 200, 255),
                ascii_char='🪼',
                catch_rate=0.09,
                description='透明优雅的海洋生物，身体柔软如凝胶。游泳时如同在水中舞蹈，美丽但可能有刺。'
            ),
            'coral': Fish(
                name='珊瑚',
                rarity='rare',
                min_length=5,
                max_length=20,
                base_price=60,
                color=(255, 100, 150),
                ascii_char='🪸',
                catch_rate=0.03,
                description='海洋中的活化石，实际上是由无数小动物组成的群体。色彩艳丽，是海洋生态系统的重要组成部分。'
            ),
            'frog': Fish(
                name='青蛙',
                rarity='uncommon',
                min_length=8,
                max_length=15,
                base_price=18,
                color=(0, 200, 0),
                ascii_char='🐸',
                catch_rate=0.11,
                description='两栖动物，既能在水中游泳也能在陆地上跳跃。叫声响亮，是池塘和湖泊的常见居民。'
            ),
            'turtle': Fish(
                name='乌龟',
                rarity='rare',
                min_length=25,
                max_length=50,
                base_price=55,
                color=(100, 150, 50),
                ascii_char='🐢',
                catch_rate=0.05,
                description='长寿的爬行动物，背负着坚硬的龟壳。游泳缓慢但持久，是智慧和长寿的象征。'
            ),
            'lizard': Fish(
                name='蜥蜴',
                rarity='uncommon',
                min_length=12,
                max_length=25,
                base_price=16,
                color=(150, 100, 50),
                ascii_char='🦎',
                catch_rate=0.08,
                description='敏捷的爬行动物，有些种类善于游泳。能够快速改变体色，是自然界的伪装高手。'
            ),
            'snake': Fish(
                name='水蛇',
                rarity='rare',
                min_length=40,
                max_length=80,
                base_price=65,
                color=(100, 100, 0),
                ascii_char='🐍',
                catch_rate=0.04,
                description='在水中游泳的蛇类，身体修长灵活。虽然看起来危险，但大多数水蛇对人类无害。'
            ),
            'crocodile': Fish(
                name='鳄鱼',
                rarity='epic',
                min_length=100,
                max_length=200,
                base_price=300,
                color=(50, 100, 50),
                ascii_char='🐊',
                catch_rate=0.008,
                description='史前时代的王者，强大的掠食者。钓到它需要极大的勇气，是真正的钓鱼传奇。'
            ),
            
            # 传说鱼类 - 金色
            'golden_carp': Fish(
                name='金鲤鱼',
                rarity='legendary',
                min_length=40,
                max_length=80,
                base_price=200,
                color=(255, 215, 0),
                ascii_char='><$$$>',
                catch_rate=0.01,
                description='传说中的金色鲤鱼，据说能够带来好运和财富。其金色鳞片在阳光下闪闪发光。'
            ),
            
            # 传说级神秘生物
            'dragon': Fish(
                name='水龙',
                rarity='legendary',
                min_length=300,
                max_length=500,
                base_price=2000,
                color=(255, 0, 0),
                ascii_char='🐉',
                catch_rate=0.001,
                description='传说中的神秘生物，拥有强大的力量和智慧。据说只有真正的勇士才能遇见它。'
            ),
            'dinosaur': Fish(
                name='恐龙',
                rarity='legendary',
                min_length=400,
                max_length=800,
                base_price=3000,
                color=(100, 50, 0),
                ascii_char='🦕',
                catch_rate=0.0005,
                description='来自远古时代的巨大生物，本应已经灭绝。能够钓到它简直是时空的奇迹。'
            ),
            'tyrannosaurus': Fish(
                name='暴龙',
                rarity='legendary',
                min_length=500,
                max_length=1000,
                base_price=5000,
                color=(150, 0, 0),
                ascii_char='🦖',
                catch_rate=0.0002,
                description='史前时代的终极掠食者，拥有可怕的力量和锋利的牙齿。这是最不可思议的钓鱼奇迹。'
            )
        }
        
        # 定义可钓到的猫咪类型
        self.cat_types = {
            # 经典猫咪系列
            'elegant_cat': CatCatch(
                name='洛芙蒂',
                personality='举止优雅，气质高贵，总是保持完美的仪态',
                rarity='uncommon',
                color=(150, 150, 150),  # 银灰色
                ascii_char='🐈',
                catch_rate=0.025
            ),
            'meng_meng_cat': CatCatch(
                name='糖果咪',
                personality='天真可爱，总是用无辜的大眼睛看着你',
                rarity='common',
                color=(255, 200, 150),  # 奶茶色
                ascii_char='🐱',
                catch_rate=0.035
            ),
            'joy_cat': CatCatch(
                name='烈焰喵',
                personality='永远充满活力，是天生的开心果',
                rarity='common',
                color=(255, 220, 100),  # 金黄色
                ascii_char='😺',
                catch_rate=0.030
            ),
            'giggly_cat': CatCatch(
                name='嘻莎',
                personality='总是在偷笑，似乎知道什么有趣的秘密',
                rarity='uncommon',
                color=(255, 180, 200),  # 粉色
                ascii_char='😸',
                catch_rate=0.020
            ),
            'lovey_cat': CatCatch(
                name='月眠夏',
                personality='容易被美好的事物迷住，眼中总是闪着星星',
                rarity='rare',
                color=(255, 100, 150),  # 玫瑰色
                ascii_char='😻',
                catch_rate=0.012
            ),
            'kissy_cat': CatCatch(
                name='亲亲猫',
                personality='非常亲近人类，喜欢用鼻子轻触表达爱意',
                rarity='uncommon',
                color=(255, 150, 100),  # 橙色
                ascii_char='😽',
                catch_rate=0.018
            ),
            'shadow_cat': CatCatch(
                name='夜影',
                personality='神秘莫测，在黑暗中行动自如，拥有不可思议的能力',
                rarity='epic',
                color=(30, 30, 30),  # 深黑色
                ascii_char='🐈‍⬛',
                catch_rate=0.008
            ),
            
            # 野生系列
            'tiger_cat': CatCatch(
                name='虎斑',
                personality='勇敢威武，拥有老虎般的气势但猫咪般的温柔',
                rarity='epic',
                color=(255, 165, 0),  # 橙色带黑纹
                ascii_char='🐅',
                catch_rate=0.006
            ),
            'mask_cat': CatCatch(
                name='盗影',
                personality='聪明狡猾，喜欢翻垃圾桶寻找宝贝，双手特别灵巧',
                rarity='rare',
                color=(120, 120, 120),  # 灰棕色
                ascii_char='🦝',
                catch_rate=0.010
            ),
            'sly_cat': CatCatch(
                name='狐媚儿',
                personality='机智过人，眼神中总是闪烁着智慧的光芒',
                rarity='rare',
                color=(255, 140, 0),  # 狐狸色
                ascii_char='🦊',
                catch_rate=0.009
            ),
            
            # 宠物系列
            'curly_cat': CatCatch(
                name='卷卷',
                personality='毛发蓬松卷曲，总是精心打理自己的外表',
                rarity='uncommon',
                color=(200, 200, 200),  # 白色
                ascii_char='🐩',
                catch_rate=0.015
            ),
            'guard_cat': CatCatch(
                name='守护者',
                personality='忠诚可靠，总是守护在主人身边，责任感很强',
                rarity='rare',
                color=(139, 69, 19),  # 棕色
                ascii_char='🐕‍🦺',
                catch_rate=0.008
            ),
            'guide_cat': CatCatch(
                name='引路星',
                personality='善于指引方向，是迷路者的好伙伴',
                rarity='rare',
                color=(255, 215, 0),  # 金色
                ascii_char='🦮',
                catch_rate=0.007
            ),
            
            # 传说系列
            'dragon_cat': CatCatch(
                name='龙吟',
                personality='传说中的龙之血脉，拥有神秘的力量和威严的气质',
                rarity='legendary',
                color=(255, 0, 0),  # 红色
                ascii_char='🐉',
                catch_rate=0.002
            ),
            'stripe_cat': CatCatch(
                name='斑纹',
                personality='身上有美丽的条纹图案，奔跑速度极快',
                rarity='epic',
                color=(255, 255, 255),  # 白色带黑纹
                ascii_char='🦓',
                catch_rate=0.004
            ),
            
            # 农场系列
            'piggy_cat': CatCatch(
                name='懒懒',
                personality='超级懒惰，一天能睡20个小时，但睡姿特别可爱',
                rarity='common',
                color=(255, 192, 203),  # 粉红色
                ascii_char='🐖',
                catch_rate=0.025
            ),
            'bleaty_cat': CatCatch(
                name='咩咩',
                personality='温顺善良，叫声像小羊一样软糯，毛发特别蓬松',
                rarity='uncommon',
                color=(255, 255, 240),  # 奶白色
                ascii_char='🐐',
                catch_rate=0.020
            ),
            'hoppy_cat': CatCatch(
                name='蹦蹦',
                personality='活泼好动，总是蹦蹦跳跳，耳朵特别长',
                rarity='uncommon',
                color=(210, 180, 140),  # 棕色
                ascii_char='🐇',
                catch_rate=0.018
            ),
            'bouncy_cat': CatCatch(
                name='跳跳喵',
                personality='跳跃能力惊人，能一跃三尺高，尾巴特别有力',
                rarity='rare',
                color=(160, 82, 45),  # 棕色
                ascii_char='🦘',
                catch_rate=0.008
            ),
            'hippo_cat': CatCatch(
                name='嘟嘟喵',
                personality='嘴巴特别大，喜欢在水中游泳，性格温和憨厚',
                rarity='epic',
                color=(128, 128, 128),  # 灰色
                ascii_char='🦛',
                catch_rate=0.005
            ),
            'camel_cat': CatCatch(
                name='沙漠行者',
                personality='能够在沙漠中生存，背上有可爱的小驼峰，很耐旱',
                rarity='rare',
                color=(210, 180, 140),  # 沙色
                ascii_char='🐫',
                catch_rate=0.007
            ),
            'moo_cat': CatCatch(
                name='哞哞喵',
                personality='体型较大但性格温顺，叫声低沉有力，黑白斑点很美丽',
                rarity='uncommon',
                color=(255, 255, 255),  # 黑白色
                ascii_char='🐂',
                catch_rate=0.015
            ),
            'antler_cat': CatCatch(
                name='森林精灵',
                personality='头上长着优美的角，动作优雅如舞者，是森林的精灵',
                rarity='epic',
                color=(139, 69, 19),  # 棕色
                ascii_char='🦌',
                catch_rate=0.006
            )
        }
        
        # 定义可钓到的垃圾和其他物品
        self.trash_types = {
            # 垃圾类 - 负价值
            'old_boot': TrashCatch(
                name='旧靴子',
                category='trash',
                rarity='common',
                value=-5,
                color=(139, 69, 19),
                ascii_char='👢',
                catch_rate=0.008,
                description='一只破旧的靴子，看起来已经在水里泡了很久。散发着奇怪的味道。'
            ),
            'old_shoe': TrashCatch(
                name='旧鞋子',
                category='trash',
                rarity='common',
                value=-3,
                color=(100, 100, 100),
                ascii_char='👟',
                catch_rate=0.010,
                description='一只丢失的运动鞋，鞋带已经腐朽。让人想知道它的主人在哪里。'
            ),
            'old_clothes': TrashCatch(
                name='旧衣服',
                category='trash',
                rarity='common',
                value=-8,
                color=(150, 150, 150),
                ascii_char='👕',
                catch_rate=0.006,
                description='一件破烂的衣服，颜色已经褪去。成为了水中生物的临时避难所。'
            ),
            'soda_bottle': TrashCatch(
                name='饮料瓶',
                category='trash',
                rarity='common',
                value=-2,
                color=(0, 150, 0),
                ascii_char='🥤',
                catch_rate=0.012,
                description='一个塑料饮料瓶，标签已经模糊不清。是水体污染的典型例子。'
            ),
            'food_wrapper': TrashCatch(
                name='食品包装',
                category='trash',
                rarity='common',
                value=-1,
                color=(255, 200, 0),
                ascii_char='🍟',
                catch_rate=0.015,
                description='快餐的包装袋，轻飘飘地漂浮在水面上。提醒人们要保护环境。'
            ),
            'old_battery': TrashCatch(
                name='旧电池',
                category='trash',
                rarity='uncommon',
                value=-15,
                color=(255, 0, 0),
                ascii_char='🔋',
                catch_rate=0.004,
                description='一节腐蚀的电池，对环境有害。需要妥善处理，不能随意丢弃。'
            ),
            'plastic_bag': TrashCatch(
                name='塑料袋',
                category='trash',
                rarity='common',
                value=-3,
                color=(255, 255, 255),
                ascii_char='🧺',
                catch_rate=0.009,
                description='一个破损的塑料袋，在水中像幽灵一样飘荡。对水生动物构成威胁。'
            ),
            'old_phone': TrashCatch(
                name='旧手机',
                category='trash',
                rarity='rare',
                value=-30,
                color=(0, 0, 0),
                ascii_char='📱',
                catch_rate=0.002,
                description='一部进水的手机，屏幕已经破碎。可能包含有价值的金属，但需要专业回收。'
            ),
            
            # 自然物品 - 低价值
            'seaweed': TrashCatch(
                name='水草',
                category='natural',
                rarity='common',
                value=1,
                color=(0, 100, 0),
                ascii_char='🌿',
                catch_rate=0.020,
                description='一束柔软的水草，是水中生态系统的重要组成部分。可以用来装饰鱼缸。'
            ),
            'stone': TrashCatch(
                name='石头',
                category='natural',
                rarity='common',
                value=0,
                color=(100, 100, 100),
                ascii_char='🪨',
                catch_rate=0.018,
                description='一块普通的石头，被水流冲刷得很光滑。虽然没有价值，但有自然之美。'
            ),
            'reed': TrashCatch(
                name='芦苇',
                category='natural',
                rarity='common',
                value=2,
                color=(200, 200, 0),
                ascii_char='🌾',
                catch_rate=0.016,
                description='一根干燥的芦苇，常见于湖边和河畔。古代人用它来做纸张。'
            ),
            'wood': TrashCatch(
                name='木头',
                category='natural',
                rarity='uncommon',
                value=5,
                color=(139, 69, 19),
                ascii_char='🪵',
                catch_rate=0.008,
                description='一截漂流木，被水流冲刷得很光滑。可以用来生火或制作小工艺品。'
            ),
            'shell': TrashCatch(
                name='贝壳',
                category='natural',
                rarity='uncommon',
                value=8,
                color=(255, 255, 200),
                ascii_char='🐚',
                catch_rate=0.006,
                description='一个美丽的贝壳，内部有珍珠般的光泽。是大自然的艺术品。'
            ),
            
            # 宝物类 - 高价值
            'old_watch': TrashCatch(
                name='旧手表',
                category='treasure',
                rarity='rare',
                value=50,
                color=(255, 215, 0),
                ascii_char='⌚',
                catch_rate=0.001,
                description='一块古老的手表，虽然停止了运转，但仍有收藏价值。可能属于某个重要的人。'
            ),
            'keys': TrashCatch(
                name='钥匙',
                category='treasure',
                rarity='uncommon',
                value=15,
                color=(192, 192, 192),
                ascii_char='🔑',
                catch_rate=0.003,
                description='一串神秘的钥匙，不知道能打开什么门。也许隐藏着某个秘密。'
            ),
            'money_bag': TrashCatch(
                name='钱袋',
                category='treasure',
                rarity='epic',
                value=200,
                color=(255, 215, 0),
                ascii_char='💰',
                catch_rate=0.0005,
                description='一个沉重的钱袋，里面装满了古老的硬币。可能是某个商人丢失的财富。'
            ),
            'gem': TrashCatch(
                name='宝石',
                category='treasure',
                rarity='legendary',
                value=500,
                color=(255, 0, 255),
                ascii_char='💎',
                catch_rate=0.0001,
                description='一颗闪闪发光的宝石，在阳光下折射出彩虹般的光芒。这是真正的宝藏！'
            )
        }
        
        # 稀有度颜色映射
        self.rarity_colors = {
            'common': (255, 255, 255),      # 白色
            'uncommon': (0, 255, 0),        # 绿色
            'rare': (0, 150, 255),          # 蓝色
            'epic': (160, 0, 255),          # 紫色
            'legendary': (255, 215, 0)      # 金色
        }
        
        # 稀有度中文名称
        self.rarity_names = {
            'common': '普通',
            'uncommon': '不常见',
            'rare': '稀有',
            'epic': '史诗',
            'legendary': '传说'
        }
    
    def catch_fish(self) -> Optional[Dict]:
        """
        尝试捕获一条鱼、猫咪或垃圾物品
        返回鱼/猫咪/垃圾的信息字典，如果没钓到返回None
        """
        # 首先检查是否钓到猫咪
        cat_result = self.try_catch_cat()
        if cat_result:
            return cat_result
        
        # 然后检查是否钓到垃圾物品
        trash_result = self.try_catch_trash()
        if trash_result:
            return trash_result
        
        # 如果没钓到猫和垃圾，尝试钓鱼
        return self.try_catch_fish()
    
    def try_catch_cat(self) -> Optional[Dict]:
        """
        尝试钓到猫咪
        """
        # 计算猫咪总概率
        total_cat_rate = sum(cat.catch_rate for cat in self.cat_types.values())
        
        # 随机判断是否钓到猫咪
        rand = random.random()
        if rand <= total_cat_rate:
            # 选择具体的猫咪类型
            cat_rand = random.random() * total_cat_rate
            current_rate = 0
            
            for cat_id, cat in self.cat_types.items():
                current_rate += cat.catch_rate
                if cat_rand <= current_rate:
                    print(f"🎣✨ 奇迹发生了！钓到了一只 {cat.name}！")
                    return {
                        'type': 'cat',
                        'id': cat_id,
                        'name': cat.name,
                        'personality': cat.personality,
                        'rarity': cat.rarity,
                        'rarity_name': self.rarity_names[cat.rarity],
                        'color': cat.color,
                        'ascii_char': cat.ascii_char,
                        'description': f"一只{self.rarity_names[cat.rarity]}的小猫咪"
                    }
        
        return None
    
    def try_catch_trash(self) -> Optional[Dict]:
        """
        尝试钓到垃圾物品
        """
        # 计算垃圾物品总概率
        total_trash_rate = sum(trash.catch_rate for trash in self.trash_types.values())
        
        # 随机判断是否钓到垃圾物品
        rand = random.random()
        if rand <= total_trash_rate:
            # 选择具体的垃圾物品类型
            trash_rand = random.random() * total_trash_rate
            current_rate = 0
            
            for trash_id, trash in self.trash_types.items():
                current_rate += trash.catch_rate
                if trash_rand <= current_rate:
                    if trash.category == 'treasure':
                        print(f"🎣💎 太幸运了！钓到了 {trash.name}！")
                    elif trash.category == 'natural':
                        print(f"🎣🌿 钓到了 {trash.name}。")
                    else:
                        print(f"🎣🗑️ 钓到了 {trash.name}...")
                    
                    return {
                        'type': 'trash',
                        'id': trash_id,
                        'name': trash.name,
                        'category': trash.category,
                        'rarity': trash.rarity,
                        'rarity_name': self.rarity_names[trash.rarity],
                        'value': trash.value,
                        'color': trash.color,
                        'ascii_char': trash.ascii_char,
                        'description': trash.description
                    }
        
        return None
    
    def try_catch_fish(self) -> Optional[Dict]:
        """
        尝试钓到鱼
        """
        # 计算鱼类总概率
        total_rate = sum(fish.catch_rate for fish in self.fish_types.values())
        
        # 随机选择
        rand = random.random() * total_rate
        current_rate = 0
        
        for fish_id, fish in self.fish_types.items():
            current_rate += fish.catch_rate
            if rand <= current_rate:
                # 钓到这种鱼，生成具体信息
                length = random.randint(fish.min_length, fish.max_length)
                
                # 根据长度调整价格
                length_ratio = (length - fish.min_length) / (fish.max_length - fish.min_length)
                price = int(fish.base_price * (1 + length_ratio * 0.5))
                
                return {
                    'type': 'fish',
                    'id': fish_id,
                    'name': fish.name,
                    'rarity': fish.rarity,
                    'rarity_name': self.rarity_names[fish.rarity],
                    'length': length,
                    'price': price,
                    'color': fish.color,
                    'ascii_char': fish.ascii_char,
                    'description': fish.description
                }
        
        # 没钓到鱼
        return None
    
    def get_fish_display_name(self, fish_info: Dict) -> str:
        """
        获取鱼、猫咪或垃圾物品的显示名称
        """
        if fish_info.get('type') == 'cat':
            return f"{fish_info['name']} ({fish_info['rarity_name']})"
        elif fish_info.get('type') == 'trash':
            value_str = f"+{fish_info['value']}" if fish_info['value'] >= 0 else str(fish_info['value'])
            return f"{fish_info['name']} ({value_str}金币, {fish_info['rarity_name']})"
        else:
            return f"{fish_info['name']} ({fish_info['length']}cm, {fish_info['rarity_name']})"
    
    def get_fish_by_id(self, fish_id: str) -> Fish:
        """
        根据ID获取鱼类信息
        """
        return self.fish_types.get(fish_id)
    
    def get_trash_by_id(self, trash_id: str) -> TrashCatch:
        """
        根据ID获取垃圾物品信息
        """
        return self.trash_types.get(trash_id) 