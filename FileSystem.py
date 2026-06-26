import hashlib
import random
import sys
import os

# md5 function
def md5(text):
    return hashlib.md5(text.encode()).hexdigest()

# test md5 on startup - required by assignment
def md5_test():
    r = md5("This is a test")
    print('MD5 ("This is a test") = ' + r)

# read salt.txt into a dict
def load_salt():
    data = {}
    if os.path.exists("salt.txt"):
        f = open("salt.txt", "r")
        for line in f:
            line = line.strip()
            if ":" in line:
                parts = line.split(":")
                data[parts[0]] = parts[1]
        f.close()
    return data

# read shadow.txt into a dict
def load_shadow():
    data = {}
    if os.path.exists("shadow.txt"):
        f = open("shadow.txt", "r")
        for line in f:
            line = line.strip()
            if ":" in line:
                parts = line.split(":")
                # format is username:hash:clearance
                data[parts[0]] = {"hash": parts[1], "clearance": int(parts[2])}
        f.close()
    return data

# check password meets requirements
def check_password(pw):
    if len(pw) < 8:
        return False, "too short, need at least 8 characters"
    hasUpper = False
    hasLower = False
    hasDigit = False
    hasSpecial = False
    special = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
    for c in pw:
        if c.isupper():
            hasUpper = True
        if c.islower():
            hasLower = True
        if c.isdigit():
            hasDigit = True
        if c in special:
            hasSpecial = True
    if not hasUpper:
        return False, "need at least one uppercase letter"
    if not hasLower:
        return False, "need at least one lowercase letter"
    if not hasDigit:
        return False, "need at least one number"
    if not hasSpecial:
        return False, "need at least one special character"
    return True, "ok"

# -i flag: create new user
def register():
    salts = load_salt()

    username = input("Username: ").strip()

    # check if already exists
    if username in salts:
        print("Error: that username already exists")
        sys.exit(1)

    # get password
    while True:
        pw1 = input("Password: ").strip()
        pw2 = input("Confirm Password: ").strip()

        if pw1 != pw2:
            print("passwords dont match, try again")
            continue

        ok, msg = check_password(pw1)
        if not ok:
            print("Invalid password: " + msg)
            print("Requirements: min 8 chars, uppercase, lowercase, number, special char")
            continue
        break

    # get clearance level
    while True:
        print("User clearance (Bell-LaPadula security levels):")
        print("  0 - Unclassified : Anyone can read, lowest sensitivity")
        print("  1 - Confidential : Low sensitivity, restricted access")
        print("  2 - Secret       : Medium sensitivity, limited personnel")
        print("  3 - Top Secret   : Highest sensitivity, strictly controlled")
        cl = input("Enter clearance (0/1/2/3): ").strip()
        if cl in ["0","1","2","3"]:
            clearance = int(cl)
            break
        print("invalid, please enter 0, 1, 2 or 3")

    # generate random 8 digit salt
    salt = str(random.randint(10000000, 99999999))

    # hash the password+salt
    hashed = md5(pw1 + salt)

    # save to salt.txt
    f = open("salt.txt", "a")
    f.write(username + ":" + salt + "\n")
    f.close()

    # save to shadow.txt
    f = open("shadow.txt", "a")
    f.write(username + ":" + hashed + ":" + str(clearance) + "\n")
    f.close()

    print("User '" + username + "' registered successfully.")

# login: no args
def login():
    salts = load_salt()
    shadows = load_shadow()

    username = input("Username: ").strip()

    if username not in salts:
        print("Error: " + username + " not found in salt.txt")
        sys.exit(1)

    password = input("Password: ").strip()

    # get their salt
    salt = salts[username]
    print(username + " found in salt.txt")
    print("salt retrieved: " + salt)
    print("hashing...")

    hashed = md5(password + salt)
    print("hash value: " + hashed)

    # check shadow
    if username not in shadows:
        print("Error: user not in shadow.txt")
        sys.exit(1)

    if hashed != shadows[username]["hash"]:
        print("Error: wrong password, authentication failed")
        sys.exit(1)

    cl = shadows[username]["clearance"]
    print("\nAuthentication for user " + username + " complete.")
    print("The clearance for " + username + " is " + str(cl) + ".")

    return username, cl

# store files in memory as dict
myfiles = {}

# load Files.store if it exists
def load_files():
    global myfiles
    if os.path.exists("Files.store"):
        f = open("Files.store", "r")
        for line in f:
            line = line.strip()
            if line.startswith("FILE:"):
                parts = line.split("|")
                name = parts[0].replace("FILE:","").strip()
                owner = parts[1].replace("OWNER:","").strip()
                level = int(parts[2].replace("LEVEL:","").strip())
                content = ""
                if len(parts) > 3:
                    content = parts[3].replace("CONTENT:","").strip()
                myfiles[name] = {"owner": owner, "level": level, "content": content}
        f.close()

# save all files to Files.store
def save_files():
    f = open("Files.store", "w")
    f.write("# FileSystem Records\n")
    for name in myfiles:
        d = myfiles[name]
        f.write("FILE:" + name + "|OWNER:" + d["owner"] + "|LEVEL:" + str(d["level"]) + "|CONTENT:" + d["content"] + "\n")
    f.close()
    print("saved to Files.store")

# bell lapadula - no read up
def can_read(user_cl, file_cl):
    return user_cl >= file_cl

# bell lapadula - no write down
def can_write(user_cl, file_cl):
    return user_cl <= file_cl

# main menu after login
def menu(username, clearance):
    while True:
        print("\nOptions: (C)reate, (A)ppend, (R)ead, (W)rite, (L)ist, (S)ave or (E)xit.")
        choice = input("Choice: ").strip().upper()

        if choice == "C":
            fname = input("Filename: ").strip()
            if fname in myfiles:
                print("file already exists")
            else:
                myfiles[fname] = {"owner": username, "level": clearance, "content": ""}
                print("created " + fname + " at level " + str(clearance))

        elif choice == "R":
            fname = input("Filename: ").strip()
            if fname not in myfiles:
                print("file not found")
            elif can_read(clearance, myfiles[fname]["level"]):
                print("Content: " + myfiles[fname]["content"])
            else:
                print("Access denied. Your clearance (" + str(clearance) + ") is below file level (" + str(myfiles[fname]["level"]) + ")")

        elif choice == "W":
            fname = input("Filename: ").strip()
            if fname not in myfiles:
                print("file not found")
            elif can_write(clearance, myfiles[fname]["level"]):
                content = input("Enter content: ").strip()
                myfiles[fname]["content"] = content
                print("written to " + fname)
            else:
                print("Access denied. Your clearance (" + str(clearance) + ") is above file level (" + str(myfiles[fname]["level"]) + ")")

        elif choice == "A":
            fname = input("Filename: ").strip()
            if fname not in myfiles:
                print("file not found")
            elif can_write(clearance, myfiles[fname]["level"]):
                content = input("Enter content to append: ").strip()
                myfiles[fname]["content"] = myfiles[fname]["content"] + " " + content
                print("appended to " + fname)
            else:
                print("Access denied. Your clearance (" + str(clearance) + ") is above file level (" + str(myfiles[fname]["level"]) + ")")

        elif choice == "L":
            if len(myfiles) == 0:
                print("no files yet")
            else:
                print("\n--- FileSystem Records ---")
                for name in myfiles:
                    print("  " + name + " | Owner: " + myfiles[name]["owner"] + " | Level: " + str(myfiles[name]["level"]))

        elif choice == "S":
            save_files()

        elif choice == "E":
            ans = input("Shut down the FileSystem? (Y)es or (N)o: ").strip().upper()
            if ans == "Y":
                print("shutting down")
                sys.exit(0)

        else:
            print("invalid option, try again")

# entry point
if __name__ == "__main__":
    md5_test()

    if len(sys.argv) > 1 and sys.argv[1] == "-i":
        register()
    else:
        load_files()
        username, clearance = login()
        menu(username, clearance)