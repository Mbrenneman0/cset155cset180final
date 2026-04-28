from flask import flash, session, request, render_template, redirect, url_for
import extensions
from Modules.Types import TableNames, Role

def route_controller(user:Role, vender:Role=None):
    
    return