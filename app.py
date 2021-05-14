from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time

# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose database
db = client['InfoSys']

# Choose collections
students = db['Students']
users = db['Users']

# Initiate Flask App
app = Flask(__name__)

users_sessions = {}

# Create Session for the User
def create_session(username):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (username, time.time())
    return user_uuid  

# Check User's Session Validity
def is_session_valid(user_uuid):
    return user_uuid in users_sessions


# ΕΡΩΤΗΜΑ 1: Δημιουργία χρήστη
@app.route('/createUser', methods=['POST'])
def create_user():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=500, mimetype='application/json')
    if data == None:
        return Response("bad request", status=500, mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete", status=500, mimetype="application/json")

    """
    Το συγκεκριμένο endpoint θα δέχεται στο body του request του χρήστη ένα json της μορφής: 

    {
        "usename": "some username", 
        "password": "a very secure password"
    }

    * Θα πρέπει να εισαχθεί ένας νέος χρήστης στο σύστημα, ο οποίος θα εισάγεται στο collection Users (μέσω της μεταβλητής users). 
    * Η εισαγωγή του νέου χρήστη, θα γίνεται μόνο στη περίπτωση που δεν υπάρχει ήδη κάποιος χρήστης με το ίδιο username. 
    * Αν γίνει εισαγωγή του χρήστη στη ΒΔ, να επιστρέφεται μήνυμα με status code 200. 
    * Διαφορετικά, να επιστρέφεται μήνυμα λάθους, με status code 400.
    """

    # Έλεγχος δεδομένων username / password
    # Αν δεν υπάρχει user με το username που έχει δοθεί. 
    # Να συμπληρώσετε το if statement.

    if users.find({"username":data["username"]}).count()==0: #Αν το username δεν υπάρχει στο collection users (.count()==0) τότε τον εισάγω
        user = {"username":data['username'], "password":data['password']}
        users.insert_one(user) #Εισαγωγή του χρήστη στο collection
        return Response(data['username'] + " was added to the MongoDB", status=200, mimetype='application/json') # Μήνυμα επιτυχίας και εμφάνιση επιτυχούς status
    
    # Διαφορετικά, αν υπάρχει ήδη κάποιος χρήστης με αυτό το username
    else:
        # Μήνυμα λάθους (Υπάρχει ήδη κάποιος χρήστης με αυτό το username)
        return Response("A user with the given email already exists", status=400, mimetype='application/json') # Εμφάνιση status αποτυχίας


# ΕΡΩΤΗΜΑ 2: Login στο σύστημα
@app.route('/login', methods=['POST'])
def login():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=500, mimetype='application/json')
    if data == None:
        return Response("bad request", status=500, mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete", status=500, mimetype="application/json")

    """
        Να καλεστεί η συνάρτηση create_session() (!!! Η ΣΥΝΑΡΤΗΣΗ create_session() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) 
        με παράμετρο το username μόνο στη περίπτωση που τα στοιχεία που έχουν δοθεί είναι σωστά, δηλαδή:
        * το data['username'] είναι ίσο με το username που είναι στη ΒΔ (να γίνει αναζήτηση στο collection Users) ΚΑΙ
        * το data['password'] είναι ίσο με το password του συγκεκριμένου χρήστη.
        * Η συνάρτηση create_session() θα επιστρέφει ένα string το οποίο θα πρέπει να αναθέσετε σε μία μεταβλητή που θα ονομάζεται user_uuid.
        
        * Αν γίνει αυθεντικοποίηση του χρήστη, να επιστρέφεται μήνυμα με status code 200. 
        * Διαφορετικά, να επιστρέφεται μήνυμα λάθους με status code 400.
    """

    # Έλεγχος δεδομένων username / password
    # Αν η αυθεντικοποίηση είναι επιτυχής. 
    # Να συμπληρώσετε το if statement.
    if users.find_one( {"$and": [ {"username":data['username']}, {"password":data['password']}] } ): # Αν υπάρχει χρήστης με ίδιο συνδυασμό username και password
        user_uuid = create_session(data['username']) # Δημιουργία του session του χρήστη
        res = {"uuid": user_uuid, "username": data['username']} # Εκχώρηση δεδομένων σε μεταβλητή res για εμφάνιση στον χρήστη, με τη βοήθεια του json.dumps()
        return Response("Authentification successful." + json.dumps(res), mimetype='application/json', status=200) # Μήνυμα επιτυχίας και εμφάνιση επιτυχούς status

    # Διαφορετικά, αν η αυθεντικοποίηση είναι ανεπιτυχής.
    else:
        # Μήνυμα λάθους (Λάθος username ή password)
        return Response("Wrong username or password.", status=400, mimetype='application/json') # Εμφάνιση status αποτυχίας


# ΕΡΩΤΗΜΑ 3: Επιστροφή φοιτητή βάσει email 
@app.route('/getStudent', methods=['GET'])
def get_student():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=500, mimetype='application/json')
    if data == None:
        return Response("bad request", status=500, mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete", status=500, mimetype="application/json")

    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα δέχεται σαν argument το email του φοιτητή και θα επιστρέφει τα δεδομένα του. 
        Να περάσετε τα δεδομένα του φοιτητή σε ένα dictionary που θα ονομάζεται student.
        
        Σε περίπτωση που δε βρεθεί κάποιος φοιτητής, να επιστρέφεται ανάλογο μήνυμα.
    """

    uuid = request.headers.get('Authorization') # Εισαγωγή uuid από τον χρήστη
    if is_session_valid(uuid) : # Αν το uuid είναι valid, τότε εκτέλεση ερωτήματος
        student = students.find_one({'email':data["email"]}) # Εύρεση μαθητή με το εισαγόμενο email
        if student != None: # Αν υπάρχει ο μαθητής
            # Η παρακάτω εντολές χρησιμοποιούνται μόνο στη περίπτωση επιτυχούς αναζήτησης φοιτητών (δηλ. υπάρχει φοιτητής με αυτό το email).
            student['_id'] = None
            return Response("User authentified - " + json.dumps(student), status=200, mimetype='application/json') # Μήνυμα επιτυχίας, στοιχείων μαθητή και εμφάνιση επιτυχούς status
        else: # Αν δεν υπάρχει ο μαθητής
            return Response("Student doesn't exist.") # Μήνυμα ότι ο μαθητής δεν υπάρχει
    else:
        return Response("User has not been authenticated.", status=401, mimetype='application/json') # Ο χρήστης δεν έχει ταυτοποιηθεί


# ΕΡΩΤΗΜΑ 4: Επιστροφή όλων των φοιτητών που είναι 30 ετών
@app.route('/getStudents/thirties', methods=['GET'])
def get_students_thirties():
    
    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 
        
        Το συγκεκριμένο endpoint θα πρέπει να επιστρέφει τη λίστα των φοιτητών οι οποίοι είναι 30 ετών.
        Να περάσετε τα δεδομένα των φοιτητών σε μία λίστα που θα ονομάζεται students.
        
        Σε περίπτωση που δε βρεθεί κάποιος φοιτητής, να επιστρέφεται ανάλογο μήνυμα και όχι κενή λίστα.
    """

    uuid = request.headers.get('Authorization') # Εισαγωγή uuid από τον χρήστη
    if is_session_valid(uuid) : # Αν το uuid είναι valid, τότε εκτέλεση ερωτήματος
        iterable = students.find({"yearOfBirth": 1991}) # Εύρεση μαθητών με ημερομηνία γέννησης το 1991 (30 ετών)
        student_list = [] # Κενή λίστα στην οποία θα περαστούν όσοι είναι 30 ετών
        for student in iterable: # Επανάληψη για κάθε μαθητή που βρήκε
            student['_id'] = None
            student_list.append(student) # Εισαγωγή μαθητή στη λίστα
        if student_list != None: # Αν η λίστα έχει άτομα, εκτύπωση μηνύματος με τη λίστα στον χρήστη
            return Response(json.dumps(student_list), status=200, mimetype='application/json') # Μήνυμα λίστας μαθητών που είναι 30 ετών και εμφάνιση επιτυχούς status
        else: # Αν η λίστα είναι κενή, τότε δεν υπάρχουν 30άριδες
            return Response("There are no students that are 30 year old.") # Μήνυμα ότι δεν υπάρχουν μαθητές που είναι 30 ετών
    else:
        return Response("User has not been authenticated.", status=401, mimetype='application/json') # Ο χρήστης δεν έχει ταυτοποιηθεί


# ΕΡΩΤΗΜΑ 5: Επιστροφή όλων των φοιτητών που είναι τουλάχιστον 30 ετών
@app.route('/getStudents/oldies', methods=['GET'])
def get_students_oldies():
    
    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει και το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 
        
        Το συγκεκριμένο endpoint θα πρέπει να επιστρέφει τη λίστα των φοιτητών οι οποίοι είναι 30 ετών και άνω.
        Να περάσετε τα δεδομένα των φοιτητών σε μία λίστα που θα ονομάζεται students.
        
        Σε περίπτωση που δε βρεθεί κάποιος φοιτητής, να επιστρέφεται ανάλογο μήνυμα και όχι κενή λίστα.
    """
    
    uuid = request.headers.get('Authorization') # Εισαγωγή uuid από τον χρήστη
    if is_session_valid(uuid) : # Αν το uuid είναι valid, τότε εκτέλεση ερωτήματος
        iterable = students.find({"yearOfBirth":{'$lte':1991}}) # Εύρεση μαθητών με ημερομηνία γέννησης κάτω του 1991 (30+ ετών)
        student_list = [] # Κενή λίστα στην οποία θα περαστούν όσοι είναι άνω των 30 ετών
        for student in iterable: # Επανάληψη για κάθε μαθητή που βρήκε
            student['_id'] = None
            student_list.append(student) # Εισαγωγή μαθητή στη λίστα
        if student_list != None: # Αν η λίστα έχει άτομα, εκτύπωση μηνύματος με τη λίστα στον χρήστη
            return Response(json.dumps(student_list), status=200, mimetype='application/json') # Μήνυμα λίστας μαθητών που είναι άνω των 30 ετών και εμφάνιση επιτυχούς status
        else:
            return Response("There are no students that are equal or older than 30 year old.") # Μήνυμα ότι δεν υπάρχουν μαθητές που είναι άνω των 30 ετών
    else:
        return Response("User has not been authenticated.", status=401, mimetype='application/json') # Ο χρήστης δεν έχει ταυτοποιηθεί


# ΕΡΩΤΗΜΑ 6: Επιστροφή φοιτητή που έχει δηλώσει κατοικία βάσει email 
@app.route('/getStudentAddress', methods=['GET'])
def get_student_address():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=500, mimetype='application/json')
    if data == None:
        return Response("bad request", status=500, mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete", status=500, mimetype="application/json")

    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει και το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα δέχεται σαν argument το email του φοιτητή. 
        * Στη περίπτωση που ο φοιτητής έχει δηλωμένη τη κατοικία του, θα πρέπει να επιστρέφεται το όνομα του φοιτητή η διεύθυνσή του(street) και ο Ταχυδρομικός Κωδικός (postcode) της διεύθυνσης αυτής.
        * Στη περίπτωση που είτε ο φοιτητής δεν έχει δηλωμένη κατοικία, είτε δεν υπάρχει φοιτητής με αυτό το email στο σύστημα, να επιστρέφεται μήνυμα λάθους. 
        
        Αν υπάρχει όντως ο φοιτητής με δηλωμένη κατοικία, να περάσετε τα δεδομένα του σε ένα dictionary που θα ονομάζεται student.
        Το student{} να είναι της μορφής: 
        student = {"name": "Student's name", "street": "The street where the student lives", "postcode": 11111}
    """

    uuid = request.headers.get('Authorization') # Εισαγωγή uuid από τον χρήστη
    if is_session_valid(uuid) : # Αν το uuid είναι valid, τότε εκτέλεση ερωτήματος
        student = students.find_one({"$and":[ {"email":data["email"]}, {"address":{"$ne":None}} ]}) # Εύρεση μαθητή με το δωθέν email και ύπαρξη διεύθυνσης
        if student != None: # Υπάρχει μαθητής
            student = {"name":student["name"], 'street':student["address"][0]["street"], 'postcode':student["address"][0]["postcode"]} # Εισαγωγή πληροφοριών μαθητή για εκτύπωση
            # Η παρακάτω εντολή χρησιμοποιείται μόνο σε περίπτωση επιτυχούς αναζήτησης φοιτητή (υπάρχει ο φοιτητής και έχει δηλωμένη κατοικία).
            return Response(json.dumps(student), status=200, mimetype='application/json') # Μήνυμα εκτύπωσης στοιχείων μαθητή και εμφάνιση επιτυχούς status
        else: # Δεν υπάρχει μαθητής που να έχει και το δωθέν email και εκχωρημένη διεύθυνση
            student = students.find_one({"email":data["email"]}) # Ελέγχω αν υπάρχει το email
            if student == None: # Αν δεν υπάρχει το email, τότε δεν υπάρχει μαθητής
                return Response("There is no student with that email.")
            else: # Αν υπάρχει το email, τότε ο συγκεκριμένος μαθητής δεν έχει περασμένη διεύθυνση
                return Response("The student with the email you entered has no address.")
    else:
        return Response("User has not been authenticated.", status=401, mimetype='application/json') # Ο χρήστης δεν έχει ταυτοποιηθεί


# ΕΡΩΤΗΜΑ 7: Διαγραφή φοιτητή βάσει email 
@app.route('/deleteStudent', methods=['DELETE'])
def delete_student():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=500, mimetype='application/json')
    if data == None:
        return Response("bad request", status=500, mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete", status=500, mimetype="application/json")

    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει και το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα δέχεται σαν argument το email του φοιτητή. 
        * Στη περίπτωση που υπάρχει φοιτητής με αυτό το email, να διαγράφεται από τη ΒΔ. Να επιστρέφεται μήνυμα επιτυχούς διαγραφής του φοιτητή.
        * Διαφορετικά, να επιστρέφεται μήνυμα λάθους. 
        
        Και στις δύο περιπτώσεις, να δημιουργήσετε μία μεταβλήτη msg (String), η οποία θα περιλαμβάνει το αντίστοιχο μήνυμα.
        Αν βρεθεί ο φοιτητής και διαγραφεί, στο μήνυμα θα πρέπει να δηλώνεται και το όνομά του (πχ: msg = "Morton Fitzgerald was deleted.").
    """

    uuid = request.headers.get('Authorization') # Εισαγωγή uuid από τον χρήστη
    if is_session_valid(uuid) : # Αν το uuid είναι valid, τότε εκτέλεση ερωτήματος
        student = students.find_one({"email":data["email"]}) # Εύρεση μαθητή με το δωθέν email
        if student != None: # Αν υπάρχει ο μαθητής, τότε διαγράφεται
            students.delete_one(student) # Διαγραφή
            st_name = student["name"] # Εκχώρηση ονόματος σε μεταβλητή
            msg = st_name + " was deleted." # Δημιουργία msg μηνύματος για εκτύπωση
            return Response(msg, status=200, mimetype='application/json') # Μήνυμα επιτυχούς διαγραφής μαθητή και εμφάνιση επιτυχούς status
        else: # Αν δεν υπάρχει μαθητής, εκτύπωσε αντίστοιχο μήνυμα
            return Response("There is no student with that email.")
    else:
        return Response("User has not been authenticated.", status=401, mimetype='application/json') # Ο χρήστης δεν έχει ταυτοποιηθεί


# ΕΡΩΤΗΜΑ 8: Εισαγωγή μαθημάτων σε φοιτητή βάσει email 
@app.route('/addCourses', methods=['PATCH'])
def add_courses():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=500, mimetype='application/json')
    if data == None:
        return Response("bad request", status=500, mimetype='application/json')
    if not "email" in data or not "courses" in data:
        return Response("Information incomplete", status=500, mimetype="application/json")

    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει και το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα δέχεται σαν argument το email του φοιτητή. Στο body του request θα πρέπει δίνεται ένα json της παρακάτω μορφής:
        
        {
            email: "an email",
            courses: [
                {'course 1': 10 }, 
                {'course 2': 3 }, 
                {'course 3': 8},
                ...
            ]
        } 
        
        Η λίστα courses έχει μία σειρά από dictionary για τα οποία τα key αντιστοιχούν σε τίτλο μαθημάτων και το value στο βαθμό που έχει λάβει ο φοιτητής σε αυτό το μάθημα.
        * Στη περίπτωση που υπάρχει φοιτητής με αυτό το email, θα πρέπει να γίνει εισαγωγή των μαθημάτων και των βαθμών τους, σε ένα νέο key του document του φοιτητή που θα ονομάζεται courses. 
        * Το νέο αυτό key θα πρέπει να είναι μία λίστα από dictionary.
        * Αν δε βρεθεί φοιτητής με αυτό το email να επιστρέφεται μήνυμα λάθους. 
    """

    uuid = request.headers.get('Authorization') # Εισαγωγή uuid από τον χρήστη
    if is_session_valid(uuid) : # Αν το uuid είναι valid, τότε εκτέλεση ερωτήματος
        student = students.find_one({"email":data["email"]}) # Εύρεση μαθητή με το δωθέν email
        if student != None: # Αν υπάρχει ο μαθητής, τότε εκχωρούνται τα μαθήματα του στα στοιχεία του
            student = students.update_one({'email':data["email"]}, {'$set': {'courses':data["courses"]}}) # set: εκχώρηση των νέων στοιχείων μαθημάτων-βαθμών
            msg = "Updated successfully" # Μήνυμα επιτυχίας σε μεταβλητή
            return Response(msg, status=200, mimetype='application/json') # Εκτύπωση του προηγούμενου μηνύματος, εμφάνιση επιτυχούς status
        else: # Αν δεν υπάρχει μαθητής, εκτύπωσε αντίστοιχο μήνυμα
            return Response('No student found with the email.', status=500, mimetype='application/json')
    else:
        return Response("User has not been authenticated.", status=401, mimetype='application/json') # Ο χρήστης δεν έχει ταυτοποιηθεί


# ΕΡΩΤΗΜΑ 9: Επιστροφή περασμένων μαθημάτων φοιτητή βάσει email
@app.route('/getPassedCourses', methods=['GET'])
def get_courses():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=500, mimetype='application/json')
    if data == None:
        return Response("bad request", status=500, mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete", status=500, mimetype="application/json")

    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει και το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα δέχεται σαν argument το email του φοιτητή.
        * Στη περίπτωση που ο φοιτητής έχει βαθμολογία σε κάποια μαθήματα, θα πρέπει να επιστρέφεται το όνομά του (name) καθώς και τα μαθήματα που έχει πέρασει.
        * Στη περίπτωση που είτε ο φοιτητής δεν περάσει κάποιο μάθημα, είτε δεν υπάρχει φοιτητής με αυτό το email στο σύστημα, να επιστρέφεται μήνυμα λάθους.
        
        Αν υπάρχει όντως ο φοιτητής με βαθμολογίες σε κάποια μαθήματα, να περάσετε τα δεδομένα του σε ένα dictionary που θα ονομάζεται student.
        Το dictionary student θα πρέπει να είναι της μορφής: student = {"course name 1": X1, "course name 2": X2, ...}, όπου X1, X2, ... οι βαθμολογίες (integer) των μαθημάτων στα αντίστοιχα μαθήματα.
    """

    uuid = request.headers.get('Authorization') # Εισαγωγή uuid από τον χρήστη
    if is_session_valid(uuid) : # Αν το uuid είναι valid, τότε εκτέλεση ερωτήματος
        student = students.find_one({"$and":[ {"email":data["email"]}, {"courses":{"$ne":None}} ]}) # Εύρεση μαθητή που έχει το δωθέν email και έχει εκχωρημένα μαθήματα
        if student != None: # Αν υπάρχει ο μαθητής, τότε εκχωρούνται τα μαθήματα του στα στοιχεία του
            student['_id'] = None
            courses = {'courses':student["courses"]} # Δημιουργία courses για να μπορούν να προσπελαστούν τα μαθήματα ένα-ένα στην επανάληψη
            passed = {} # Δημιουργία κενού dictionary, στο οποίο θα εισαχθούν τα περασμένα μαθήματα του μαθητή
            for course in courses.values(): # Για κάθε μάθημα, επανάληψη
                for item in course:
                    for grade in item:
                        if item.get(grade) >= 5: # Αν ο βαθμός είναι περασμένος, τότε εκχωρείται στο dictionary passed
                            passed[grade] = item.get(grade)
            if len(passed) != 0: # Αν το dictionary περασμένων έχει μαθήματα
                return Response(student["name"] + json.dumps(passed), status=200, mimetype='application/json') # Εκτύπωση επιτυχούς μηνύματος και επιτυχούς status)
            else: # Αν η λίστα περασμένων είναι άδεια
                return Response("The student hasn't passed any courses.")
        else: # Δεν υπάρχει μαθητής που να έχει και το δωθέν email και τα μαθήματα
            student = students.find_one({"email":data["email"]}) # Ελέγχω αν υπάρχει το email
            if student == None: # Αν δεν υπάρχει το email, τότε δεν υπάρχει μαθητής
                return Response("There is no student with that email.")
            else: # Αν υπάρχει το email, τότε ο συγκεκριμένος μαθητής δεν έχει εισάγει μαθήματα
                return Response("The student with the email you entered has no courses.")
    else:
        return Response("User has not been authenticated.", status=401, mimetype='application/json') # Ο χρήστης δεν έχει ταυτοποιηθεί


# Εκτέλεση flask service σε debug mode, στην port 5000. 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)