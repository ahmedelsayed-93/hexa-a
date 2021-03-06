from client.client import Client
from flask import Blueprint, render_template, session, request
from authentication.authenticator import login_required, group_access_level

api = Client()
page = 'assignments'

assignments_pages = Blueprint('assignments_pages', __name__)

@assignments_pages.before_request
@login_required
def client_auth(**kwargs):
    api.set_auth_header('Bearer %s' % session['jwt'])

@assignments_pages.route("/groups/<groupId>/assignments")
@login_required
@group_access_level('member')
def AssignmentsPage(** kwargs):
    username = kwargs.get('username')
    groupId = kwargs.get('groupId')
    group = api.groups.get(groupId=groupId).json()
    assignments = api.groups.assignments.list(groupId).json()
    return render_template('group/assignment/assignments.html', page=page, group=group, assignments=assignments)

@assignments_pages.route("/groups/<groupId>/assignments/<assignmentId>")
@login_required
@group_access_level('member')
def AssignmentPage(** kwargs):
    username = kwargs.get('username')
    user_role = kwargs.get('user_role')
    groupId = kwargs.get('groupId')
    assignmentId = kwargs.get('assignmentId')
    filters = dict(request.args)
    subtab = request.args.get('subtab', 'details')

    group = api.groups.get(groupId=groupId).json()
    assignment = api.groups.assignments.get(groupId, assignmentId).json()

    if subtab == 'submissions':
        limit = request.args.get('limit', 25, int)
        page_ = request.args.get('page', 1, int)
        params = {'limit':limit, 'page':page_}
        for arg in request.args:
            if arg in ['username', 'testsuite', 'status']:
                params[arg] = request.args.get(arg)
        
        
        members = api.groups.members.list(groupId).json()        
        submissions = api.groups.assignments.submissions(groupId, assignmentId, params=params).json()

        return render_template(
            'group/assignment/assignment.html', 
            page=page, 
            subtab='submissions', 
            group=group, 
            assignment=assignment, 
            submissions=submissions, 
            members=members,
            filters=filters
        )

    elif subtab == 'settings':
        testsuites = []
        if user_role == 'admin':
            testsuites = api.groups.testsuites.list(groupId).json()

        return render_template(
            'group/assignment/assignment.html', 
            page=page, 
            subtab='settings', 
            group=group, 
            assignment=assignment,
            testsuites=testsuites
        )


    else:
        return render_template(
            'group/assignment/assignment.html', 
            page=page, 
            subtab='details', 
            group=group, 
            assignment=assignment
        )
        

@assignments_pages.route("/groups/<groupId>/assignments/new")
@login_required
@group_access_level('admin')
def NewAssignmentPage(**kwargs):
    groupId = kwargs.get('groupId', None)
    group = api.groups.get(groupId=groupId).json()
    return render_template('group/new_assignment.html', page=page, group=group)

@assignments_pages.route("/groups/<groupId>/assignments/<assignmentId>/edit")
@login_required
@group_access_level('admin')
def EditAssignmentPage(**kwargs):
    groupId = kwargs.get('groupId', None)
    assignmentId = kwargs.get('assignmentId', None)
    group = api.groups.get(groupId=groupId).json()
    assignment = api.groups.assignments.get(groupId, assignmentId).json()
    return render_template('group/edit_assignment.html', page=page, group=group, assignment=assignment)