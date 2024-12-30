from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
import os
from datetime import datetime, timedelta
from models import db, Snippet, Tag, URL, Todo, TodoStatus, Note

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///snippets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Main dashboard route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/network')
def network_utilities():
    return render_template('network/index.html')

@app.route('/password-generator')
def password_generator():
    return render_template('password_generator.html')

# Placeholder routes for existing functionality
@app.route('/repos')
def list_repos():
    return render_template('repos/index.html', repos=[])

@app.route('/repos/new')
def new_repo():
    return render_template('repos/new.html')

@app.route('/hosts')
def list_hosts():
    return render_template('hosts/index.html', hosts=[])

@app.route('/hosts/new')
def new_host():
    return render_template('hosts/new.html')

@app.route('/notes')
def list_notes():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return render_template('notes/index.html', notes=notes)

@app.route('/notes/new', methods=['GET', 'POST'])
def new_note():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        note = Note(
            title=title,
            content=content
        )
        
        db.session.add(note)
        db.session.commit()
        flash('Note created successfully!', 'success')
        return redirect(url_for('list_notes'))
        
    return render_template('notes/new.html')

# Certificate routes
@app.route('/certificates')
def list_certificates():
    return render_template('certificates/index.html', certificates=[])

@app.route('/certificates/new')
def new_certificate():
    return render_template('certificates/new.html')

@app.route('/certificates/<int:id>')
def view_certificate(id):
    return render_template('certificates/view.html')

@app.route('/certificates/<int:id>/edit')
def edit_certificate(id):
    return render_template('certificates/edit.html')

# Snippets routes
@app.route('/snippets')
def list_snippets():
    snippets = Snippet.query.order_by(Snippet.created_at.desc()).all()
    return render_template('snippets/index.html', snippets=snippets)

@app.route('/snippets/new', methods=['GET', 'POST'])
def new_snippet():
    if request.method == 'POST':
        title = request.form.get('title')
        command = request.form.get('command')
        description = request.form.get('description')
        usage_notes = request.form.get('usage_notes')
        example = request.form.get('example')
        expected_output = request.form.get('expected_output')
        failure_scenarios = request.form.get('failure_scenarios')
        tag_names = request.form.get('tags', '').split(',')

        snippet = Snippet(
            title=title,
            command=command,
            description=description,
            usage_notes=usage_notes,
            example=example,
            expected_output=expected_output,
            failure_scenarios=failure_scenarios
        )

        # Handle tags
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                snippet.tags.append(tag)

        db.session.add(snippet)
        db.session.commit()
        flash('Snippet created successfully!', 'success')
        return redirect(url_for('list_snippets'))

    return render_template('snippets/new.html')

@app.route('/snippets/<int:id>')
def view_snippet(id):
    snippet = Snippet.query.get_or_404(id)
    return render_template('snippets/view.html', snippet=snippet)

@app.route('/snippets/<int:id>/edit', methods=['GET', 'POST'])
def edit_snippet(id):
    snippet = Snippet.query.get_or_404(id)
    
    if request.method == 'POST':
        snippet.title = request.form.get('title')
        snippet.command = request.form.get('command')
        snippet.description = request.form.get('description')
        snippet.usage_notes = request.form.get('usage_notes')
        snippet.example = request.form.get('example')
        snippet.expected_output = request.form.get('expected_output')
        snippet.failure_scenarios = request.form.get('failure_scenarios')
        
        # Update tags
        snippet.tags.clear()
        tag_names = request.form.get('tags', '').split(',')
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                snippet.tags.append(tag)

        db.session.commit()
        flash('Snippet updated successfully!', 'success')
        return redirect(url_for('view_snippet', id=snippet.id))

    return render_template('snippets/edit.html', snippet=snippet)

@app.route('/snippets/<int:id>/delete', methods=['POST'])
def delete_snippet(id):
    snippet = Snippet.query.get_or_404(id)
    db.session.delete(snippet)
    db.session.commit()
    flash('Snippet deleted successfully!', 'success')
    return redirect(url_for('list_snippets'))

@app.route('/snippets/search')
def search_snippets():
    query = request.args.get('q', '')
    tag = request.args.get('tag', '')
    
    snippets = Snippet.query
    
    if query:
        snippets = snippets.filter(
            db.or_(
                Snippet.title.ilike(f'%{query}%'),
                Snippet.command.ilike(f'%{query}%'),
                Snippet.description.ilike(f'%{query}%')
            )
        )
    
    if tag:
        snippets = snippets.filter(Snippet.tags.any(Tag.name == tag))
    
    snippets = snippets.order_by(Snippet.created_at.desc()).all()
    return render_template('snippets/index.html', snippets=snippets, query=query, tag=tag)

# URL routes
@app.route('/urls')
def list_urls():
    urls = URL.query.order_by(URL.created_at.desc()).all()
    return render_template('urls/index.html', urls=urls)

@app.route('/urls/new', methods=['GET', 'POST'])
def new_url():
    if request.method == 'POST':
        url = request.form.get('url')
        title = request.form.get('title')
        notes = request.form.get('notes')
        tag_names = request.form.get('tags', '').split(',')

        url_entry = URL(
            url=url,
            title=title,
            notes=notes
        )

        # Handle tags
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                url_entry.tags.append(tag)

        db.session.add(url_entry)
        db.session.commit()
        flash('URL added successfully!', 'success')
        return redirect(url_for('list_urls'))

    return render_template('urls/new.html')

@app.route('/urls/<int:id>')
def view_url(id):
    url = URL.query.get_or_404(id)
    return render_template('urls/view.html', url=url)

@app.route('/urls/<int:id>/edit', methods=['GET', 'POST'])
def edit_url(id):
    url = URL.query.get_or_404(id)
    
    if request.method == 'POST':
        url.url = request.form.get('url')
        url.title = request.form.get('title')
        url.notes = request.form.get('notes')
        
        # Update tags
        url.tags.clear()
        tag_names = request.form.get('tags', '').split(',')
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                url.tags.append(tag)

        db.session.commit()
        flash('URL updated successfully!', 'success')
        return redirect(url_for('view_url', id=url.id))

    return render_template('urls/edit.html', url=url)

@app.route('/urls/<int:id>/delete', methods=['POST'])
def delete_url(id):
    url = URL.query.get_or_404(id)
    db.session.delete(url)
    db.session.commit()
    flash('URL deleted successfully!', 'success')
    return redirect(url_for('list_urls'))

@app.route('/urls/search')
def search_urls():
    query = request.args.get('q', '')
    tag = request.args.get('tag', '')
    
    urls = URL.query
    
    if query:
        urls = urls.filter(
            db.or_(
                URL.title.ilike(f'%{query}%'),
                URL.url.ilike(f'%{query}%'),
                URL.notes.ilike(f'%{query}%')
            )
        )
    
    if tag:
        urls = urls.filter(URL.tags.any(Tag.name == tag))
    
    urls = urls.order_by(URL.created_at.desc()).all()
    return render_template('urls/index.html', urls=urls, query=query, tag=tag)

# Todo routes
@app.route('/todos')
def list_todos():
    status_filter = request.args.get('status')
    week_filter = request.args.get('week')
    
    todos = Todo.query
    
    if status_filter:
        todos = todos.filter(Todo.status == TodoStatus(status_filter))
    
    if week_filter:
        week_start = datetime.strptime(week_filter, '%Y-%m-%d')
        week_end = week_start + timedelta(days=7)
        todos = todos.filter(Todo.created_at.between(week_start, week_end))
    
    todos = todos.order_by(Todo.due_date.asc(), Todo.created_at.desc()).all()
    return render_template('todos/index.html', todos=todos, statuses=TodoStatus)

@app.route('/todos/new', methods=['GET', 'POST'])
def new_todo():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = TodoStatus(request.form.get('status', 'pending'))
        notes = request.form.get('notes')
        due_date = request.form.get('due_date')
        
        if due_date:
            due_date = datetime.strptime(due_date, '%Y-%m-%d')
        
        todo = Todo(
            title=title,
            description=description,
            status=status,
            notes=notes,
            due_date=due_date
        )
        
        db.session.add(todo)
        db.session.commit()
        flash('Todo created successfully!', 'success')
        return redirect(url_for('list_todos'))
    
    return render_template('todos/new.html', statuses=TodoStatus)

@app.route('/todos/<int:id>')
def view_todo(id):
    todo = Todo.query.get_or_404(id)
    return render_template('todos/view.html', todo=todo)

@app.route('/todos/<int:id>/edit', methods=['GET', 'POST'])
def edit_todo(id):
    todo = Todo.query.get_or_404(id)
    
    if request.method == 'POST':
        todo.title = request.form.get('title')
        todo.description = request.form.get('description')
        todo.status = TodoStatus(request.form.get('status'))
        todo.notes = request.form.get('notes')
        due_date = request.form.get('due_date')
        
        if due_date:
            todo.due_date = datetime.strptime(due_date, '%Y-%m-%d')
        
        db.session.commit()
        flash('Todo updated successfully!', 'success')
        return redirect(url_for('view_todo', id=todo.id))
    
    return render_template('todos/edit.html', todo=todo, statuses=TodoStatus)

@app.route('/todos/<int:id>/delete', methods=['POST'])
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    flash('Todo deleted successfully!', 'success')
    return redirect(url_for('list_todos'))

@app.route('/todos/report')
def todo_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status')
    
    todos = Todo.query
    
    if start_date and end_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        todos = todos.filter(Todo.created_at.between(start, end))
    
    if status:
        todos = todos.filter(Todo.status == TodoStatus(status))
    
    todos = todos.order_by(Todo.created_at.desc()).all()
    return render_template('todos/report.html', todos=todos, statuses=TodoStatus)

if __name__ == '__main__':
    app.run(debug=True, port=5010)
