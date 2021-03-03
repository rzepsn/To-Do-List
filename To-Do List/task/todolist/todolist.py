from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import and_
from datetime import datetime, timedelta

Base = declarative_base()  # it returns DeclarativeMeta class, that all table classes should inherit from


class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer,primary_key=True)
    task = Column(String)
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return "{}".format(self.task)


class ToDoList:
    prompt = "1) Today's tasks\n2) Week's tasks\n3) All tasks\n4) Missed tasks\n5) Add task\n6) Delete task\n0) Exit\n"

    def __init__(self):
        self.engine = create_engine('sqlite:///todo.db?check_same_thread=False')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.running = True
        self.main()

    def get_tasks_per_day(self, dtime):
        task_rows = self.session.query(Task).filter(Task.deadline == dtime).all()
        return task_rows

    def get_all_tasks(self):
        task_rows = self.session.query(Task).order_by(Task.deadline).all()
        return task_rows

    def get_missed_tasks(self):
        task_rows = self.session.query(Task).filter(Task.deadline< datetime.today()).order_by(Task.deadline).all()
        return task_rows

    def print_tasks_today(self):
        today = datetime.today()
        print()
        print("Today: {}\n".format(today.strftime('%#d %b')))
        task_rows = self.get_tasks_per_day(today.date())
        if len(task_rows) == 0:
            print("Nothing to do!")
        else:
            i = 1
            for task in task_rows:
                print("{}. {}".format(i, task))
                i += 1
        print()

    def print_tasks_week(self):
        today = datetime.today()
        print()
        i = 0
        for i in range(7):
            weekday = today + timedelta(days=i)
            task_rows = self.get_tasks_per_day(weekday.date())
            print()
            #Monday 27 Apr:
            print(weekday.strftime('%A %#d %b'))
            if len(task_rows) == 0:
                print("Nothing to do!")
            else:
                n = 1
                for task in task_rows:
                    print("{}. {}".format(n, task.task))
                    n += 1
        print()

    def print_all_tasks(self):
        task_rows = self.get_all_tasks()
        if len(task_rows) == 0:
            print("Nothing to do!")
        else:
            n = 1
            for t in task_rows:
                #4. Order a new keyboard. 1 May
                print("{}. {}. {}".format(n, t.task, t.deadline.strftime('%#d %b')))
                n += 1
        print()
        return task_rows

    def print_missed_tasks(self):
        task_rows = self.get_missed_tasks()
        if len(task_rows) == 0:
            print("Nothing to do!")
        else:
            for t in task_rows:
                # 4. Order a new keyboard. 1 May
                print("{}. {}. {}".format(t.id, t.task, t.deadline.strftime('%#d %b')))
        print()
        return task_rows

    def add_task(self):
        print()
        print("Enter task")
        task_description = input()
        print("Enter deadline")
        task_deadline = input()
        task_deadline = datetime.strptime(task_deadline, '%Y-%m-%d')
        new_row = Task(task=task_description, deadline=task_deadline)
        self.session.add(new_row)
        self.session.commit()
        print("The task has been added!")
        print()

    def delete_task(self):
        print()
        print("\nChoose the number of the task you want to delete:")
        task_rows = self.print_all_tasks()
        task_number = int(input())
        self.session.delete(task_rows[task_number - 1])
        self.session.commit()
        print("The task has been deleted!")
        print()

    def finish(self):
        self.running = False
        print()
        print("Bye")

    def main(self):
        while self.running:
            selected_option = input(self.prompt)
            if selected_option == '1':
                self.print_tasks_today()
            elif selected_option == '2':
                self.print_tasks_week()
            elif selected_option == '3':
                print("\nAll tasks:")
                self.print_all_tasks()
            elif selected_option == '4':
                print("\nMissed tasks:")
                self.print_missed_tasks()
            elif selected_option == '5':
                self.add_task()
            elif selected_option == '6':
                self.delete_task()
            elif selected_option == '0':
                self.finish()


ToDoList()