# GRADING.py
# ===== Mastermind (Java) ===============
import sys
import subprocess
sys.path.append(".")
sys.path.append("../resource/lib/public")
from stdio_tools import *
from java_ast_tools import *
from name_tools import *
from asserts import *
from grader_tools import *
from shutil import copyfile
import os
import re

# import the Vocareum API library
import voc_v2

# extract the grading/report file names
grd_file = sys.argv[1]
rep_file = sys.argv[2]
# instantiate vocareum grader
voc_grader = voc_v2.Grader(grd_file, rep_file)
# turn off dumping of stdout/stderr to the Student Report
voc_grader.suppress_stdout()
# wrap vocareum grader
MyGrader = Grader(voc_grader)
# Set up Grading Criteria
# ----------------------------------------
# Syntax                  (10) - Auto Graded
# Naming                  (10) - Auto Graded
# Class Implementation    (30) - Auto Graded
# Main Logic              (30) - Auto Graded
# Correct Output          (20) - Human Graded
# ----------------------------------------
MyGrader.add_criterion("Syntax",                  10, pass_fail=False)
MyGrader.add_criterion("Naming",                  10, pass_fail=False)
MyGrader.add_criterion("Class Implementation",    30, pass_fail=False)
MyGrader.add_criterion("Main Logic",              30, pass_fail=False)
MyGrader.add_criterion("Correct Output",          20, pass_fail=False)

PASS = True
FAIL = False

def get_compiler_error_messages():
    result = subprocess.run('javac *.java', shell=True, 
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    
    compiler_error_messages = result.stdout
    return compiler_error_messages

def count_compiler_errors():
    compiler_error_messages = get_compiler_error_messages()
    
    if len(compiler_error_messages) == 0:
        return 0

    last_line = compiler_error_messages.split('\n')[-2]
    parts = last_line.split()
    error_count = int(parts[0])

    return error_count

def count_classes(profile):
    return profile.get_all_classes().count()

def count_total_characters(profile):
    return profile.get_total_file_size()

def class_field_meets_specs(a_class, access, name, datatype):
    # name
    if name not in a_class.fields.get_names():
        MyGrader.add_report_string('   !!!   ' + a_class.name + ' is missing required field: ' + name)
        return False
    
    field =  a_class.fields.get_by_name(name)
    # access
    if field.access != access:
        MyGrader.add_report_string('   !!!   ' + a_class.name + '.' + name + ' field has incorrect access modifier')
        return False
    
    # datatype
    if field.datatype != datatype:
        MyGrader.add_report_string('   !!!   ' + a_class.name + '.' + name + ' field has incorrect data type')
        return False
            
    return True

def class_method_meets_specs(a_class, access, name, param_types, return_type):
    # name
    if name not in a_class.methods.get_names():
        MyGrader.add_report_string('   !!!   Missing required method: ' + name)
        return False
    
    method =  a_class.methods.get_by_name(name)
    # access
    if method.access != access:
        MyGrader.add_report_string('   !!!   Method "' + name + '" has incorrect access modifier')
        return False
    
    # return type
    if method.return_type != return_type:
        MyGrader.add_report_string('   !!!   Method "' + name + '" has incorrect return type')
        return False
    
    actual_param_types = " ".join([param.datatype for param in method.parameters])
    if actual_param_types != param_types:
        MyGrader.add_report_string('   !!!   Method "' + name + '" has incorrect parameter list')
        return False
    
    return True
    
def mastermind_class_specs_met(profile):
    specs_met = 'none'
    spect_met_count = 0
    
    if not "Mastermind" in profile.get_all_class_names():
        return 'none'
    
    mastermind_class = profile.get_class_by_name("Mastermind")
    
    # FIELDS
    #   - secretNumber: int
    if class_field_meets_specs(mastermind_class, "private", "secretNumber", "int"):
        spect_met_count += 1
    #   - guessCount: int
    if class_field_meets_specs(mastermind_class, "private", "guessCount", "int"):
        spect_met_count += 1
    
    # METHODS
    #   + Mastermind() <<default constructor>>
    if mastermind_class.constructors.count() > 0:
        spect_met_count += 1
    #  + pickNewSecretNumber() 
    if class_method_meets_specs(mastermind_class, "public", "pickNewSecretNumber", "", "void"):
        spect_met_count += 1
    #   + makeGuess(guess: int): int
    if class_method_meets_specs(mastermind_class, "public", "makeGuess", "int", "int"):
        spect_met_count += 1
    #   + getGuessCount(): int
    if class_method_meets_specs(mastermind_class, "public", "getGuessCount", "", "int"):
        spect_met_count += 1
    #   - generateSecretNumber(): int
    if class_method_meets_specs(mastermind_class, "private", "generateSecretNumber", "", "int"):
        spect_met_count += 1
    #   - getRandomDigit(): int
    if class_method_meets_specs(mastermind_class, "private", "getRandomDigit", "", "int"):
        spect_met_count += 1
    
    if spect_met_count >= 1:
        specs_met = 'some'
    if spect_met_count >= 4:
        specs_met = 'most'
    if spect_met_count >= 8:
        specs_met = 'all'
        
    return specs_met

def test_get_syntax_points(profile):
    syntax_points = 10
    
    error_count = count_compiler_errors()
    code_compiles = error_count == 0
    class_count = count_classes(profile)
    character_count = count_total_characters(profile)
    minimal_code = class_count >= 1 and character_count >= 400;
                       
    if code_compiles and minimal_code:
        syntax_points = 10
    elif minimal_code and error_count <= 1:
        syntax_points = 8
    elif minimal_code and error_count <= 3:
        syntax_points = 6
    elif minimal_code:
        syntax_points = 4
    else: # There is no code to evaluate
        syntax_points = 2
    
    return syntax_points

def test_get_naming_points(profile):
    style_points = 2
        
    # Variable Names
    variable_names = profile.get_all_local_variable_names()
    variable_names += profile.get_all_field_names()
    if 'args' in variable_names:
        variable_names.remove('args')
    
    var_name_analysis = Names(variable_names)
    
    var_names_inconsistent = (
        var_name_analysis.some_start_with_smalls() 
        and var_name_analysis.some_start_with_caps()
        or
        var_name_analysis.some_have_humps() 
        and var_name_analysis.some_have_underscores()
    )
    
    count_short_names = var_name_analysis.select_with_len_less_than(4).count()
    
    # Method Names
    method_names = profile.get_all_method_names()
    if 'main' in method_names:
        method_names.remove('main')
        
    method_name_analysis = Names(method_names)
    
    method_names_inconsistent = (
        method_name_analysis.some_start_with_smalls() 
        and method_name_analysis.some_start_with_caps()
        or
        method_name_analysis.some_have_humps() 
        and method_name_analysis.some_have_underscores()
    )
    
    count_short_names += method_name_analysis.select_with_len_less_than(4).count()
    
    count_all_names = var_name_analysis.count() + method_name_analysis.count()
    
    if count_short_names > count_all_names // 2 and not var_names_inconsistent or not method_names_inconsistent:
        style_points = 4
        
    if count_short_names <= count_all_names // 2 and not var_names_inconsistent or not method_names_inconsistent:
        style_points = 6
        
    if count_short_names <= 2 and not var_names_inconsistent or not method_names_inconsistent:
        style_points = 8
        
    if count_short_names <= 1 and not var_names_inconsistent and not method_names_inconsistent:
        style_points = 10
    
    return style_points

def test_class_implementation_points(profile):
    classes_implementation_points = 2
    
    specs_met_mastermind_class = mastermind_class_specs_met(profile)
        
    if specs_met_mastermind_class == 'some':
        classes_implementation_points = 6  
        
    if specs_met_mastermind_class == 'most':
        classes_implementation_points = 8   
        
    if specs_met_mastermind_class == 'all':
        classes_implementation_points = 10       
    
    return classes_implementation_points

def test_main_logic_points(profile):
    main_logic_points = 2
    declares_mastermind_variable = False
    loop_count = 0;
    
    if "main" not in profile.get_all_method_names():
        return 2
    
    main_method = profile.get_all_methods().get_by_name("main");
    
    for variable in main_method.local_variables:
        if variable.datatype == "Mastermind":
            declares_mastermind_variable = True
            
    loop_count = main_method.get_loop_count()
    
    if declares_mastermind_variable or loop_count >= 1:
        main_logic_points = 6  
        
    if declares_mastermind_variable and loop_count >= 1:
        main_logic_points = 8
        
    if loop_count >= 2:
        main_logic_points = 8  
        
    if declares_mastermind_variable and loop_count >= 2:
        main_logic_points = 10
     
    return main_logic_points

def grade():
    if count_compiler_errors() > 0:
        MyGrader.add_report_string('='*62)
        MyGrader.add_report_string("Code does not compile!!!")
        MyGrader.add_report_string("Student submission cannot be graded.")
        MyGrader.add_report_string("----- COMPILER ERROR MESSAGES -----")
        MyGrader.add_report_string(get_compiler_error_messages())
        MyGrader.add_report_string('-'*62)
        
        return
        
    profile = make_profile('./')
    
    # Grading Criteria
    # ----------------------------------------
    # Syntax                  (10) - Auto Graded
    # Naming                  (10) - Auto Graded
    # Class Implementation    (30) - Auto Graded
    # Main Logic              (30) - Auto Graded
    # Correct Output          (20) - Human Graded
    # ----------------------------------------
    
    # Syntax (10) - Auto Graded
    syntax_points = test_get_syntax_points(profile) * 1
    MyGrader.criterion("Syntax").set_score(syntax_points)
    syntax_report_string = ('Syntax (' + str(syntax_points) + '/10)')
    
    # Naming (10) - Auto Graded
    naming_points = test_get_naming_points(profile) * 1
    MyGrader.criterion("Naming").set_score(naming_points)
    style_report_string = ('Naming (' + str(naming_points) + '/10)')
    
    # Class Implementation (40) - Auto Graded 
    class_implementation_points = test_class_implementation_points(profile) * 3
    MyGrader.criterion("Class Implementation").set_score(class_implementation_points)
    classes_implementation_report_string = ('Class Implementation (' + str(class_implementation_points) + '/30)')
    
    # Main Logic (20) - Auto Graded 
    main_logic_points = test_main_logic_points(profile) * 3
    MyGrader.criterion("Main Logic").set_score(main_logic_points)
    main_logic_report_string = ('Main Logic (' + str(main_logic_points) + '/30)')
    
    # Correct Output (10) - Human Graded 
    correctness_report_string = ('Correct Output (??/20) To be Graded by Instructor/Grader')

    # Write report
    MyGrader.add_report_string('')
    MyGrader.add_report_string(syntax_report_string)
    MyGrader.add_report_string(style_report_string)
    MyGrader.add_report_string(classes_implementation_report_string)
    MyGrader.add_report_string(main_logic_report_string)
    MyGrader.add_report_string(correctness_report_string)
    MyGrader.add_report_string('-'*62)

    # code size
    MyGrader.add_report_string('Code size: ' + str(profile.get_total_file_size()) + ' characters.')
    # UML classes
    for java_class in profile.get_all_classes():
        MyGrader.add_report_string(java_class.get_uml())
    # local Variables
    MyGrader.add_report_string(' -- Local Variable Names --')
    for name in profile.get_all_local_variable_names():
        MyGrader.add_report_string('    ' + name)

MyGrader.add_report_string('-'*62)
MyGrader.add_report_string('Grading ...')
MyGrader.add_report_string('-'*62)

grade()

MyGrader.add_report_string('-'*62)
MyGrader.add_report_string('Grading Complete')
MyGrader.add_report_string('-'*62)

MyGrader.write_grade_summary()
MyGrader.commit_scores()
