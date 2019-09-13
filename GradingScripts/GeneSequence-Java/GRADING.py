# GRADING.py
# ===== Gene Sequencing (Java) ===============


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
# Class Implementation    (70) - Auto Graded
# Correctness             (20) - Human Graded
# ----------------------------------------
MyGrader.add_criterion("Syntax",                  10, pass_fail=False)
MyGrader.add_criterion("Class Implementation",    70, pass_fail=False)
MyGrader.add_criterion("Correctness",             20, pass_fail=False)

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

    try:
        error_count = int(parts[0])
    except:
        error_count = 0
        MyGrader.add_report_string('='*62)
        MyGrader.add_report_string("----- COMPILER ERROR MESSAGES -----")
        MyGrader.add_report_string(compiler_error_messages)
        MyGrader.add_report_string('-'*62)

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
    
def get_DNASequence_class_specs_points(profile):
    class_specs_points = 0
    
    MyGrader.add_report_string('='*62)
    MyGrader.add_report_string("----- DNASequence Class Implementation -----")
    
    if not "DNASequence" in profile.get_all_class_names():
        return 0
    else:
        class_specs_points += 3
    
    DNASequence_class = profile.get_class_by_name("DNASequence")
    
    # FIELDS
    # - dnaArray : char[]
    if class_field_meets_specs(DNASequence_class, "private", "dnaArray", "char[]"):
        class_specs_points += 1
    else:
        MyGrader.add_report_string('---FAIL--- - dnaArray : char[]')
    
    # METHODS
    # + DNASequence(dnaString : String) <<constructor>>
    if DNASequence_class.constructors.count() > 0:
        class_specs_points += 1
    else:
        MyGrader.add_report_string('---FAIL--- + DNASequence(dnaString : String) <<constructor>>')
    # - findStartCodon(startIndex : int) : int
    if class_method_meets_specs(DNASequence_class, "private", "findStartCodon", "int", "int"):
        class_specs_points += 1
    else:
        MyGrader.add_report_string('---FAIL--- - findStartCodon(startIndex : int) : int')
    # - findStopCodon(startIndex : int) : int
    if class_method_meets_specs(DNASequence_class, "private", "findStopCodon", "int", "int"):
        class_specs_points += 1
    else:
        MyGrader.add_report_string('---FAIL--- - findStopCodon(startIndex : int) : int')
    # + extractGenes() : ArrayList<DNASequence>
    if class_method_meets_specs(DNASequence_class, "public", "extractGenes", "", "ArrayList"):
        class_specs_points += 1
    else:
        MyGrader.add_report_string('---FAIL--- + extractGenes() : ArrayList<DNASequence>')
    # + equals(other : DNASequence) : boolean
    if class_method_meets_specs(DNASequence_class, "public", "equals", "DNASequence", "boolean"):
        class_specs_points += 1
    else:
        MyGrader.add_report_string('---FAIL--- + equals(other : DNASequence) : boolean')
    # + toString() : String
    if class_method_meets_specs(DNASequence_class, "public", "toString", "", "String"):
        class_specs_points += 1
    else:
        MyGrader.add_report_string('---FAIL--- + toString() : String')
        
        
    MyGrader.add_report_string('-'*62)
    
    return class_specs_points

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

def test_classes_implementation_points(profile):
    classes_implementation_points = 2
    
    classes_implementation_points = get_DNASequence_class_specs_points(profile)
    
    
    return classes_implementation_points

def test_main_logic_points(profile):
    main_logic_points = 2
    
     
    return main_logic_points

def grade():
    if count_compiler_errors() > 0:
        MyGrader.add_report_string('='*62)
        MyGrader.add_report_string("Code does not compile!!!")
        MyGrader.add_report_string("Student submission cannot be graded.")
        MyGrader.add_report_string("----- COMPILER ERROR MESSAGES -----")
        MyGrader.add_report_string(get_compiler_error_messages())
        MyGrader.add_report_string('-'*62)
        MyGrader.write_grade_summary()
        MyGrader.commit_scores()
        
        return
        
    profile = make_profile('./')
    
    # Grading Criteria
    # ----------------------------------------
    # Syntax                  (10) - Auto Graded
    # Class Implementation    (70) - Auto Graded
    # Correctness             (20) - Auto Graded
    # ----------------------------------------
    
    # Syntax (10) - Auto Graded
    syntax_points = test_get_syntax_points(profile) * 1
    MyGrader.criterion("Syntax").set_score(syntax_points)
    syntax_report_string = ('Syntax (' + str(syntax_points) + '/10)')
    
    # Classes Implementation (70) - Auto Graded 
    classes_implementation_points = test_classes_implementation_points(profile) * 7
    MyGrader.criterion("Class Implementation").set_score(classes_implementation_points)
    class_implementation_report_string = ('Class Implementation (' + str(classes_implementation_points) + '/70)')
    
    # Correctness (20) - Human Graded 
    correctness_report_string = ('Correctness (??/20) To be Graded by Instructor/Grader')

    # Write report
    MyGrader.add_report_string('='*62)
    MyGrader.add_report_string(syntax_report_string)
    MyGrader.add_report_string(class_implementation_report_string)
    MyGrader.add_report_string(correctness_report_string)
    
    MyGrader.add_report_string('-'*62)
    MyGrader.write_grade_summary()
    
    MyGrader.add_report_string('-'*62)

    # UML classes
    for java_class in profile.get_all_classes():
        MyGrader.add_report_string(java_class.get_uml())

    # commit report
    MyGrader.commit_scores()

grade()