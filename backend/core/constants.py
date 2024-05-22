from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import IntegerChoices


class LodgementSize(IntegerChoices):
    ONE_PLUS_ONE = 1, "1+1"
    TWO_PLUS_ONE = 2, "2+1"


class LodgementType(IntegerChoices):
    SEQUENTIAL_ALLOCATION = 1, "Sıra Tahsisli"
    SERVICE_ALLOCATION = 2, "Hizmet Tahsisli"
    DUTY_ALLOCATION = 3, "Görev Tahsisli"


class ApplicationStatus(IntegerChoices):
    IN_PROGRESS = 1, "In Progress"
    PENDING = 2, "Pending"
    APPROVED = 3, "Approved"
    REJECTED = 4, "Rejected"
    RE_UPLOAD = 5, "Re Upload"
    CANCELLED = 6, "Cancelled"
    ASSIGNED = 7, "Assigned"


class AssignmentStatus(IntegerChoices):
    LOCKED = 1, "Locked"
    ACTIVE = 2, "Active"
    CANCELLED = 3, "Cancelled"
    FINISHED = 4, "Finished"


class FormType(IntegerChoices):
    SCORING = 1, "4 No'lu Cetvel"


class FormItemTypes(IntegerChoices):
    INTEGER = 1, "Integer"
    BOOLEAN = 2, "Boolean"
    TEXT = 3, "Text"


SIRA_TAHSIS_4_NOLU_CETVEL_FORM = [
    {
        "label": "Kaç tane gazi ve şehit yakınınız var?",
        "caption": "Gaziler ile şehit yakınlarının (eş, çocuk, anne, baba ve kardeş) her biri için (+40) puan",
        "field_type": FormItemTypes.INTEGER,
        "point": 40,
    },
    {
        "label": "Ailenizde kaç yüzde kırk ve üzerinde engelli birey var?",
        "caption": "Yüzde kırk ve üzerinde engelli olduğunu yetkili sağlık kurullarından alınan rapor ile belgelendiren engelli personel ile kanunen bakmakla mükellef bulunduğu ve konutta birlikte oturacağı her bir engelli aile ferdi (eş ve çocuk dahil) için (+40) puan",
        "field_type": FormItemTypes.INTEGER,
        "point": 40,
    },
    {
        "label": "Ailenize ait oturmaya elverişli başka il veya ilçede kaç konutunuz var?",
        "caption": "Personelin kendisinin, eşinin, çocuğunun ve kanunen bakmakla mükellef bulunduğu ve konutta birlikte oturacağı aile fertlerinden, aynı il veya ilçede (i) bendi kapsamı dışında kalan yerler ile başka il veya ilçelerde oturmaya elverişli konutu olanların her konut için (-10) puan",
        "field_type": FormItemTypes.INTEGER,
        "point": -10,
    },
    {
        "label": "Ailenize ait oturmaya elverişli aynı il veya ilçede kaç konutunuz var?",
        "caption": "Personelin kendisinin, eşinin, çocuğunun ve kanunen bakmakla mükellef bulunduğu ve konutta birlikte oturacağı aile fertlerinden, konutun bulunduğu il veya ilçenin belediye ve mücavir alan sınırları içinde oturmaya elverişli konutu olanların her konut için (-15) puan",
        "field_type": FormItemTypes.INTEGER,
        "point": -15,
    },
    {
        "label": "Ailenizin yıllık geliri ekte belirtilen miktarı geçiyor mu?",
        "caption": """Personelin, aylık ve özlük hakları ile ilgili gelirleri hariç olmak üzere, kendisinin ve kanunen bakmakla mükellef bulunduğu ve konutta birlikte oturacağı aile fertlerinin, konut kira gelirleri dışındaki diğer tüm sürekli gelirlerinin yıllık toplamının, 15.000 gösterge rakamının memur maaş katsayısı ile çarpımı sonucu bulunacak miktarı geçmesi halinde (-1) puan""",
        "field_type": FormItemTypes.BOOLEAN,
        "point": -1,
    },
    {
        "label": "Ailenizde eşiniz ve çocuklarınız dışında bakmaya mükellef olduğunuz kaç kişi var?",
        "caption": "Personelin, eşi ve çocukları dışında, kanunen bakmakla mükellef bulunduğu ve konutta birlikte oturacağı her aile ferdi için (+1) puan",
        "field_type": FormItemTypes.INTEGER,
        "point": 1,
    },
    {
        "label": "Ailenizde bakmakla yükümlü olduğunuz kaç çocuğunuz var? (Maksimum 2)",
        "caption": "Personelin kanunen bakmakla yükümlü olduğu çocuklarının her biri için (+3) puan, (yalnız iki çocuğa kadar)",
        "field_type": FormItemTypes.INTEGER,
        "point": 3,
    },
    {
        "label": "Eşiniz var mı?",
        "caption": "Personelin eşi için (+6) puan",
        "field_type": FormItemTypes.BOOLEAN,
        "point": 6,
    },
    {
        "label": "Daha önce Kamu Konutları Kanunu kapsamında kaç yıl bir konutta ikamet ettiniz?",
        "caption": "Personelin, 2946 sayılı Kamu Konutları Kanunu kapsamında olan kurum ve kuruluşlarda, daha önce konuttan yararlandığı her yıl için (-3) puan",
        "field_type": FormItemTypes.INTEGER,
        "point": -3,
    },
    {
        "label": "Kamu kurum ve kuruluşlarında geçen hizmet süreniz kaç yıl?",
        "caption": "Personelin 2946 sayılı Kamu Konutları Kanunu kapsamına giren kurum ve kuruluşlarda geçen hizmet süresinin her yılı için (+5) puan",
        "field_type": FormItemTypes.INTEGER,
        "point": 5,
    },
]


def days_until(target_date):
    if target_date is None:
        return "No available lodgements."
    # Get the current date and time
    current_date = datetime.now(target_date.tzinfo)

    delta = relativedelta(target_date, current_date)

    if delta.years > 0:
        return f"in {delta.years} years, {delta.months} months and {delta.days} days"
    elif delta.months > 0:
        return f"in {delta.months} months and {delta.days} days"
    else:
        return f"in {delta.days} days"
