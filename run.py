import pkg_resources, sys, subprocess

def check_reqs():
    missing = []
    try:
        with open("requirements.txt", "r") as requirements_file:
            for line in requirements_file:
                try:
                    pkg_resources.require(line)
                except pkg_resources.DistributionNotFound as e:
                    missing.append(e.req.key)
    except FileNotFoundError:
        print("No requirements file found; can not verify if requirements are available.")
        print("To skip this check and run anyway, run file with the argument \"-y\".")
        return False
    if len(missing) > 0:
        print("Some dependencies were not found.")
        try:
            pkg_resources.require("pip")
        except pkg_resources.DistributionNotFound:
            print("Pip was not found on this system, and these dependencies must be manually installled.")
            print("They are listed in requirements.txt in this directory.\n")
            print("The unfound dependencies are:")
            for miss in missing:
                print("    ", miss)
            return False
        print("Pip was detected on this system.")
        print("Would you like to automatically install all missing dependencies?")
        result = input().strip().lower()[0]
        if result == "y":
            subprocess.call([sys.executable, "-m", "pip", "install", *missing])
        else:
            print("Pip was not used to install the dependencies.")
            print("These dependencies can be found in requirements.txt.")
            print("Please install the below dependencies manually.\n")
            print("The unfound dependencies are:")
            for miss in missing:
                print("    ", miss)
        return False
    return True

def main(args):
    skip_req_check = False
    for arg in args:
        if arg.strip() == "-y":
            skip_req_check = True
    if not skip_req_check:
        if not check_reqs():
            return False
    import gui
    gui.main()

if __name__ == "__main__":
    main(sys.argv[1:])