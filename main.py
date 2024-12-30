from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty

import sqlite3


class TaskItem(BoxLayout):
    task = StringProperty() # For binding in .kv file
    task_id = NumericProperty()


class ToDoListApp(App):
    def build(self):
        self.connection = sqlite3.connect('to-do_list.db')
        self.cursor = self.connection.cursor()

        ''' Default table name. '''
        self.table_name = 'to_do_list'
        self.check_table_existence()

        return Builder.load_file('to-do_list.kv')
    

    ''' Create the default table if it doesn't exists yet. '''
    def check_table_existence(self):
        self.cursor.execute(
            ''' SELECT name FROM sqlite_master
                WHERE type="table" AND name=? ''', (self.table_name,))
        
        table_exists = self.cursor.fetchone()
        if not table_exists:
            self.create_table()
        else:
            pass
    

    ''' Create the default table. '''
    def create_table(self):
        self.cursor.execute(
            f'''CREATE TABLE {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                status INTEGER)''')
        self.connection.commit()


    ''' Status of completion can be True or False '''
    def insert_new_task(self, task, status=0):
        # Check for repeating tasks.
        same_tasks = self.check_repeated_tasks(task)

        if same_tasks != 0:
            print('This task already exists.')
        else:
            self.cursor.execute(
                f'''INSERT INTO {self.table_name} (task, status) VALUES (?, ?)
                ''', (task, status))
            
            print('Task inserted correctly')
            self.connection.commit()
        

    def add_task(self, task_text):
        if task_text.strip():
            self.insert_new_task(task_text)
            self.root.ids.task_input.text = '' # Clear input field.
            self.refresh_task_list()
        else:
            print('Task cannot be empty!')


    def retrieve_tasks(self):
        self.cursor.execute(f"SELECT * FROM {self.table_name}")
        tasks = self.cursor.fetchall()
        return tasks
    

    def check_repeated_tasks(self, task):
        ''' Search for repeated tasks '''
        self.cursor.execute(
            f'''SELECT * FROM {self.table_name} WHERE task = ?
            ''', (task,))

        repeated_tasks = self.cursor.fetchall()
        return len(repeated_tasks)
    

    def refresh_task_list(self):
        tasks = self.retrieve_tasks() # Get tasks from the database.
        # Populate the RecycleView with data
        self.root.ids.task_list.data = [
            {'task': task[1], 'status': task[2]} for task in tasks
        ]


    ''' Select task by ID '''
    def select_task(self, id):
        self.cursor.execute(
            f'''SELECT * FROM {self.table_name} WHERE id = ?
            ''', (id,))
        
        selected_task = self.cursor.fetchone()
        return selected_task


    def toggle_status(self, id):
        self.cursor.execute(
            f'''UPDATE {self.table_name} SET status = 1 - status WHERE id = ?
            ''', (id,))

        self.refresh_task_list()
        self.connection.commit()


    def delete_task(self, id):
        ''' Select the task first. '''
        selected_task = self.select_task(id)

        if selected_task != None:
            self.cursor.execute(
                f'''DELETE FROM {self.table_name} WHERE id = ?
                ''', (id,))
            self.connection.commit()
            print('Task deleted successfully!')
        else:
            print('There are no tasks left with that ID')
        
        self.refresh_task_list()
    

    def on_stop(self):
        self.connection.close()


if __name__ == '__main__':
    ToDoListApp().run()