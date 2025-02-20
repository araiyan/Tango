<a href="http://autolabproject.com">
  <img src="images/autolab_banner.svg" width="380px" height="100px">
</a>

# Tango

Tango is a standalone RESTful Web service that runs and manages jobs. A job is a set of files that must satisfy the following constraints:

1. There must be exactly one `Makefile` that runs the job.
2. The output for the job should be printed to stdout.

Example jobs are provided for the user to peruse in `clients/`. Tango has a [REST API](https://docs.autolabproject.com/tango-rest/) which is used for job submission.

Upon receiving a job, Tango will copy all of the job's input files into a VM, run `make`, and copy the resulting output back to the host machine. Tango jobs are run in pre-configured VMs. Support for various Virtual Machine Management Systems (VMMSs) like KVM, Docker, or Amazon EC2 can be added by implementing a high level [VMMS API](https://docs.autolabproject.com/tango-vmms/) that Tango provides.

A brief overview of the Tango respository:

- `tango.py` - Main tango server
- `jobQueue.py` - Manages the job queue
- `jobManager.py` - Assigns jobs to free VMs
- `worker.py` - Shepherds a job through its execution
- `preallocator.py` - Manages pools of VMs
- `vmms/` - VMMS library implementations
- `restful_tango/` - HTTP server layer on the main Tango

Tango was developed as a distributed grading system for [Autolab](https://github.com/autolab/Autolab) at Carnegie Mellon University and has been extensively used for autograding programming assignments in CMU courses.

## Using Tango

Please feel free to use Tango at your school/organization. If you run into any problems with the steps below, you can reach the core developers at `autolab-dev@andrew.cmu.edu` and we would be happy to help.

1. [Follow the steps to set up Tango](https://docs.autolabproject.com/installation/tango/).
2. [Read the documentation for the REST API](https://docs.autolabproject.com/tango-rest/).
3. [Read the documentation for the VMMS API](https://docs.autolabproject.com/tango-vmms/).
4. [Test whether Tango is set up properly and can process jobs](https://docs.autolabproject.com/tango-cli/).

## Stress Testing Tango

To stress test Tango by running a large number of submissions, use `stressTest.py`. Currently, this is not a feature on the master branch. To use this feature, go on the `copy-in`.

### Setting up the testing directory

Create your testing directory by copying the 　`sample_test` directory into the `my_tests` directory.

```
cp -r sample_tests my_tests/<Test Name>
```

A brief overview of the testing directory

- `input` - Directory to put your input files
- `output` - Directory for the autograder output for each of the test submissions
- `<Test Name>.yaml` - Yaml file to configure the stress test
- `expected_output.txt` - Expected JSON output of the autograder
- `summary.txt` - Summary of the autograder outputs
- `log.txt` - Log of the submissions

First, rename the `sample_test.yaml` to be `<Test Name>.yaml`

```
mv sample_test.yaml <Test Name>.yaml
```

Next, update the Yaml file.

```yaml
num_submissions: 5
submission_delay: 0.1
autograder_image: <Autograding Image>
output_file: log.txt
tango_port: 3001
cli_path: <Path to Tango>/clients/tango-cli.py
instance_type: <Instance Type>
timeout: 180
ec2: True
expected_output: expected_output.txt
stop_before:
```

After creating the Yaml file, copy the `autograde-Makefile`, `autograde.tar` and the file to submit in the `input` directory.

### Running the stress test

```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
cd <Path to Tango>/tests
python3 stressTest.py --test_dir my_tests/<Test Name>
```

## Python 2 Support

Tango now runs on Python 3. However, there is a legacy branch [master-python2](https://github.com/autolab/Tango/tree/master-python2) which is a snapshot of the last Python 2 Tango commit for legacy reasons. You are strongly encouraged to upgrade to the current Python 3 version of Tango if you are still on the Python 2 version, as future enhancements and bug fixes will be focused on the current master.

We will not be backporting new features from `master` to `master-python2`.

## Contributing to Tango

1. [Fork the Tango repository](https://github.com/autolab/Tango).
2. Create a local clone of the forked repo.
3. Install [pre-commit](https://pre-commit.com/) from pip, and run `pre-commit install` to set up Git pre-commit linting scripts.
4. Make a branch for your feature and start committing changes.
5. Create a pull request (PR).
6. Address any comments by updating the PR and wait for it to be accepted.
7. Once your PR is accepted, a reviewer will ask you to squash the commits on your branch into one well-worded commit.
8. Squash your commits into one and push to your branch on your forked repo.
9. A reviewer will fetch from your repo, rebase your commit, and push to Tango.

Please see [the git linear development guide](https://github.com/edx/edx-platform/wiki/How-to-Rebase-a-Pull-Request) for a more in-depth explanation of the version control model that we use.

## License

Tango is released under the [Apache License 2.0](http://opensource.org/licenses/Apache-2.0).
