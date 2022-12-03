from src.tasks.scheduler import scheduler

def test_task(*args):
    '''Test task to check if shedule is working correctly'''
    ...

# q: loop over dict python
for task, args in tasks.items():
    scheduler.add_job(task, args, trigger='interval', seconds=5)
    

