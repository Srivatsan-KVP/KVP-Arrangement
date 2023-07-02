from app.models import *
import csv, uuid, pandas

TEACHER_FIELDS = ['uid', 'name', 'post']
TABLE_FIELDS = ['uid','day','1','2','3','4','5','6','7','8']


# MIGRATIONS

def __writeCSV(f, rows: list[dict[str, str]], fields: list[str]):
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

def migrateTeachers():
    with open('teacher-migrate.csv', 'w') as f:
        rows = []
        for teacher in Teacher.objects.all():
            rows.append({
                    'uid': teacher.uid.hex,
                    'name': teacher.name,
                    'post': teacher.post
                }
            )

        __writeCSV(f, rows, TEACHER_FIELDS)

def migrateTT():
    with open('tt-migrate.csv', 'w') as f:
        rows = []
        for table in Table.objects.all():
            rows.append({
                'uid': table.teacher.uid.hex,
                'day': table.day,
                '1': table.p1, '2': table.p2, '3': table.p3, '4': table.p4,
                '5': table.p5, '6': table.p6, '7': table.p7, '8': table.p8
            })

        __writeCSV(f, rows, TABLE_FIELDS)

def writeToDB():
    with open('teacher-migrate.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(row)
            try:
                Teacher(uid=uuid.UUID(row['uid']), name=row['name'], post=row['post']).save()
            except:
                print('TEACHER:', row['uid'])

    with open('tt-migrate.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            Table(
                teacher=Teacher.objects.get(uid=uuid.UUID(row['uid'])),
                day=row['day'],
                p1=row['1'], p2=row['2'], p3=row['3'], p4=row['4'],
                p5=row['5'], p6=row['6'], p7=row['7'], p8=row['8'],
            ).save()



# UTILS 

def fixFormat():
    for t in Teacher.objects.all():
        t.name = ' '.join(t.name.split())
        t.save()
    
    for entry in Table.objects.all():
        entry.trim()

def __getMapping() -> dict[str, Teacher]:
    mapping: dict[str, Teacher] = {}
    with open('0.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            name = ' '.join(row[1].split())
            mapping[name] = Teacher.objects.get(name=name)

    return mapping

def getClass(row: list[str], period: int) -> str:
    if not row[period+1]:
        return row[period]
    return row[period+1]

def exportToCSV():
    for day in range(6):
        if day == 4: continue
        pandas.read_excel('./tt.xlsx', sheet_name=day).to_csv(f'{day}.csv', index=False)

def parseTT():
    mapping = __getMapping()
    for day in range(6):
        if day == 4: continue
        with open(f'{day}.csv') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                Table.objects.filter(teacher=mapping[' '.join(row[1].split())], day=day).delete()
                entry = Table(
                    teacher=mapping[' '.join(row[1].split())],
                    day=day,
                    p1=getClass(row, 1),p2=getClass(row, 2),p3=getClass(row, 3),p4=getClass(row, 4),
                    p5=getClass(row, 5),p6=getClass(row, 6),p7=getClass(row, 7),p8=getClass(row, 8),
                )
                entry.trim()
                