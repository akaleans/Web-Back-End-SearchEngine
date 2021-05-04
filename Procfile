# foreman start -m gateway=1,users=3,timelines=3,user-queries=3,timeline-queries=3
# gateway: python3 -m bottle --bind=localhost:$PORT --debug --reload gateway
users: python3 -m bottle --bind=localhost:$PORT --debug --reload users
timelines: python3 -m bottle --bind=localhost:$PORT --debug --reload timelines
dms: python3 -m bottle --bind=localhost:$PORT --debug --reload dms
se: python3 -m bottle --bind=localhost:$PORT --debug --reload se
