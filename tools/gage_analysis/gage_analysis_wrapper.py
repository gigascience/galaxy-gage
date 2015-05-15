"""
gage_analysis_wrapper.py
A wrapper script for the GAGE analysis
Author Peter Li peter@gigasciencejournal.com
"""

import sys
import optparse
import os
import tempfile
import shutil
import subprocess


def stop_err(msg):
    sys.stderr.write('%s\n' % msg)
    sys.exit()


def cleanup_before_exit(tmp_dir):
    if tmp_dir and os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)


def __main__():
    # Parse command line
    parser = optparse.OptionParser()

    # Input params
    parser.add_option('', '--ref_fasta', dest='ref_fasta')
    parser.add_option('', '--contig_fasta', dest='contig_fasta')
    parser.add_option('', '--scaffold_fasta', dest='scaffold_fasta')

    # Output
    parser.add_option('', '--outfile', dest='outfile')
    opts, args = parser.parse_args()

    # Might need to write inputs to a temporary directory
    # Also rename their file extensions to .fasta, etc
    dirpath = tempfile.mkdtemp(prefix="tmp-gage-")
    print dirpath

    ref_data = open(opts.ref_fasta, 'r')
    ref_file = open(dirpath + "/ref.fasta", "w")
    for line in ref_data:
        ref_file.write(line)
    ref_data.close()
    ref_file.close()

    contig_data = open(opts.contig_fasta, 'r')
    contig_file = open(dirpath + "/contig.fasta", "w")
    for line in contig_data:
        contig_file.write(line)
    contig_data.close()
    contig_file.close()

    scaf_data = open(opts.scaffold_fasta, 'r')
    scaf_file = open(dirpath + "/scaf.fasta", "w")
    for line in scaf_data:
        scaf_file.write(line)
    scaf_data.close()
    scaf_file.close()

    # Set up command line call
    cmd = "getCorrectnessStats.sh %s %s %s > %s" % (dirpath + "/ref.fasta", dirpath + "/contig.fasta", dirpath + "/scaf.fasta", opts.outfile)

    # Run
    try:
        tmp_out_file = tempfile.NamedTemporaryFile(dir=dirpath).name
        tmp_stdout = open(tmp_out_file, 'w')
        tmp_err_file = tempfile.NamedTemporaryFile().name
        tmp_stderr = open(tmp_err_file, 'w')

        proc1 = subprocess.Popen(args=cmd, shell=True, cwd=dirpath, stdout=tmp_stdout, stderr=subprocess.STDOUT)
        returncode1 = proc1.wait()
        print cmd

        tmp_stderr.close()
        #  get stderr, allowing for case where it's very large
        tmp_stderr = open(tmp_err_file, 'r')
        stderr = ''
        buffsize = 1048576
        try:
            while True:
                stderr += tmp_stderr.read(buffsize)
                if not stderr or len(stderr) % buffsize != 0:
                    break
        except OverflowError:
            pass
        tmp_stdout.close()
        tmp_stderr.close()
        if returncode1 != 0:
            raise Exception, stderr

    except Exception, e:
        raise Exception, 'Problem performing GAGE analysis process ' + str(e)

    # Clean up temp files
    # cleanup_before_exit(dirpath)
#     stop_err('Error in running GAGE evaluation from %s' % (str(e)))

    # Check results in output file
    if os.path.getsize(opts.outfile) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__":
    __main__()
