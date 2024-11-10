#
# JobManager - Thread that assigns jobs to worker threads
#
# The job manager thread wakes up every so often, scans the job list
# for new unassigned jobs, and tries to assign them.
#
# Assigning a job will try to get a preallocated VM that is ready,
# otherwise will pass 'None' as the preallocated vm.  A worker thread
# is launched that will handle things from here on. If anything goes
# wrong, the job is made dead with the error.
#

import copy
import time
import logging
import threading

from datetime import datetime

import tango  # Written this way to avoid circular imports
from config import Config
from tangoObjects import TangoQueue
from worker import Worker
from preallocator import Preallocator
from jobQueue import JobQueue


class JobManager(object):
    def __init__(self, queue):
        self.daemon = True
        self.jobQueue = queue
        self.preallocator = self.jobQueue.preallocator
        self.vmms = self.preallocator.vmms
        self.log = logging.getLogger("JobManager")
        # job-associated instance id
        self.nextId = 10000
        self.running = False

    def start(self):
        if self.running:
            return
        thread = threading.Thread(target=self.__manage)
        thread.daemon = True
        thread.start()

    def run(self):
        if self.running:
            return
        self.__manage()

    def _getNextID(self):
        """_getNextID - returns next ID to be used for a job-associated
        VM.  Job-associated VM's have 5-digit ID numbers between 10000
        and 99999.
        """
        id = self.nextId
        self.nextId += 1
        if self.nextId > 99999:
            self.nextId = 10000
        return id

    def __manage(self):
        self.running = True
        while True:
            # Blocks until we get a next job
            print("WAIT JOB")
            job = self.jobQueue.getNextPendingJob()
            print("new job ", job)
            self.log.info("JOB ACCESS %s" % job.accessKeyId)
            if not job.accessKey and Config.REUSE_VMS:
                vm = None
                while vm is None:
                    vm = self.jobQueue.reuseVM(job)
                    # Sleep for a bit and then check again
                    time.sleep(Config.DISPATCH_PERIOD)

            try:
                # if the job has specified an account
                # create an VM on the account and run on that instance
                if job.accessKeyId:
                    from vmms.ec2SSH import Ec2SSH

                    self.log.info("EC2SSH init")
                    vmms = Ec2SSH(job.accessKeyId, job.accessKey)
                    newVM = copy.deepcopy(job.vm)
                    newVM.id = self._getNextID()
                    try:
                        preVM = vmms.initializeVM(newVM)
                    except Exception as e:
                        self.log.error("ERROR initialization VM: %s", e)
                    if not preVM:
                        raise BaseException("preVM is NIL!")
                        # TODO: EXCEPTION HANDLING
                else:
                    # Try to find a vm on the free list and allocate it to
                    # the worker if successful.
                    if Config.REUSE_VMS:
                        preVM = vm
                    else:
                        preVM = self.preallocator.allocVM(job.vm.name)
                    vmms = self.vmms[job.vm.vmms]  # Create new vmms object

                if preVM.name is not None:
                    self.log.info(
                        "Dispatched job %s:%d to %s [try %d]"
                        % (job.name, job.id, preVM.name, job.retries)
                    )
                else:
                    self.log.info(
                        "Unable to pre-allocate a vm for job job %s:%d [try %d]"
                        % (job.name, job.id, job.retries)
                    )

                job.appendTrace(
                    "%s|Dispatched job %s:%d [try %d]"
                    % (datetime.utcnow().ctime(), job.name, job.id, job.retries)
                )
                print("Hello")
                # Mark the ßob assigned
                self.jobQueue.assignJob(job.id, preVM)
                print("Hello 3")
                Worker(job, vmms, self.jobQueue, self.preallocator, preVM).start()
                print("Hello 2")

            except Exception as err:
                self.log.error("job failed during creation %d %s" % (job.id, str(err)))
                self.jobQueue.makeDead(job.id, str(err))


if __name__ == "__main__":

    if not Config.USE_REDIS:
        print(
            "You need to have Redis running to be able to initiate stand-alone\
         JobManager"
        )
    else:
        tango = tango.TangoServer()
        tango.log.debug("Resetting Tango VMs")
        tango.resetTango(tango.preallocator.vmms)
        for key in tango.preallocator.machines.keys():
            tango.preallocator.machines.set(key, [[], TangoQueue(key)])
        jobs = JobManager(tango.jobQueue)

        print("Starting the stand-alone Tango JobManager")
        jobs.run()
