import json
from worker import Worker
from function import Function
from package import Package
from paSch import PaSch


def main():
    # list of workers

    workers = [{"worker_id": "1", "threshold": 100},
               {"worker_id": "2", "threshold": 50},
               {"worker_id": "3", "threshold": 150}]

    global_workers = []
    global_hashworkers = []
    for x in workers:
        global_workers.append(Worker(x["worker_id"], x["threshold"]))
        global_hashworkers.append(x["worker_id"])

    # bhai implement karna consistent hash idhar
    # print(global_workers)

    # list of fn

    func_file = open('registry/functions.json')
    fn = json.load(func_file)

    global_fn = []
    for x in fn:
        global_fn.append(
            Function(x["function_id"], x["function_imports"], x["function_size"]))

    # list of packages

    pkgs_file = open('registry/packages.json')
    pkgs = json.load(pkgs_file)

    global_pkgs = []
    for x in pkgs:
        global_pkgs.append(
            Package(x["package_id"], x["package_size"])
        )

    # fn execution instruction
    fn_inst = [{"fid:": "foo", "timestamp": 0},
               {"fid:": "bar", "timestamp": 1},
               {"fid:": "foo", "timestamp": 2},
               {"fid:": "foo", "timestamp": 3},
               {"fid:": "bar", "timestamp": 2}]

    # now we have all our inputs ready, create instance of scheduler intitalise the scheduler
    scheduler = PaSch(global_hashworkers, global_workers,
                      global_fn, global_pkgs)

    while True:
        print("\n")
        print("1. Add a new worker.")
        #print("2. Update an existing worker's threshold.")
        print("3. Remove a worker.")
        #print("4. View all workers.")
        print("5. View all functions in the registry.")
        print("6. View all packages in the registry.")
        print("7. Execute a function")
        print("8. Current state of system")
        print("9. Cache hits and miss")
        print("0. Exit")
        print("\n")
        option = int(input("Choose an option: "))
        print("\n")
        match option:
            case 1:
                w_id = input("Enter worker id: ")
                thres = int(input("Enter worker's threshold: "))
                scheduler.addWorker(Worker(w_id,thres))

                print("Worker {} successfully added!".format(w_id))
            # case 2:
                
            #     w_id = input("Enter worker id: ")
            #     thres = int(input("Enter worker's threshold: "))
            #     for i, worker in enumerate(workers):
            #         if w_id == worker["worker_id"]:
            #             worker["threshold"] = thres
            #             break
            #     print("Worker {} successfully updated!".format(w_id))
            case 3:
                w_id = input("Enter worker id: ")
                # for i, worker in enumerate(workers):
                #     if w_id == worker["worker_id"]:
                #         del workers[i]
                # print("Worker {} successfully removed!".format(w_id))
                scheduler.removeWorker(w_id)
            # case 4:
            #     print("Workers: ", workers)
            case 5:
                print("Functions: ", fn)
            case 6:
                print("Packages: ", pkgs)
            case 7:
                f_id = input("Enter the function id: ")
                t_stamp = int(input("Enter the timestamp: "))
                print(scheduler.assignWorker(f_id, t_stamp))
                
                print("Function {} successfully executed!".format(f_id))
            case 8:
                t_stamp = int(input("Enter the timestamp: "))
                print(scheduler.getWorkerDetails(t_stamp))
            case 9:
                details = scheduler.getCacheHitAndMissDetails()
                print(details)
            case 0:
                exit()
            case default:
                continue

if __name__ == "__main__":
    main()
