#!/usr/bin/env python3

import sys
import argparse
from typing import Dict, List, Set, Tuple, Generator


class KmerCount:
    """
    Counts K-mers in sequence data and generates histogram data.
    
    This class handles the counting of k-mers from FastQ files and
    converts the data into histogram format for analysis.
    """
    
    def __init__(self, kLength: int, fileN: str, OutF: str):
        """
        Initialize the KmerCount object.
        
        Args:
            kLength: Length of k-mers to analyze
            fileN: Input FastQ filename
            OutF: Output filename base (without extension)
        """
        self.kLength = kLength
        self.fileN = fileN
        self.OutF = OutF
        self.kDict: Dict[str, int] = {}
        self.fDict: Dict[int, int] = {}
        self.fList: List[int] = []

    def kCount(self, mseq: str):
        """
        Count k-mers in a given sequence.
        
        Args:
            mseq: Input sequence to analyze
        """
        self.seq = mseq
        
        # Iterate through sequence to find all k-mers
        for i in range(len(self.seq) - self.kLength + 1):
            kmer = self.seq[i:i + self.kLength]
            if 'N' not in kmer:
                self.kDict[kmer] = self.kDict.get(kmer, 0) + 1

    def addSequence(self):
        """
        Process sequences from FastQ file and generate histogram data.
        
        This is the main workflow function that:
        1. Reads sequences from FastQ file
        2. Counts k-mers
        3. Generates histogram data
        4. Writes results to output file
        """
        myReader = FastQreader(self.fileN)
        
        print("Working on counting KMers...")
        for _, seq in myReader.readFastQ():
            self.kCount(seq)
            
        print("Working on Producing Histogram Data...")
        self.fDiction()
        
        print("Writing...")
        self.kWrite()
        print("Done!")

    def fDiction(self):
        """
        Convert k-mer count data into histogram data.
        
        Creates frequency distribution of k-mer occurrences.
        """
        # Get unique frequency values
        self.valueset = set(self.kDict.values())
        
        # Count occurrences of each frequency
        for freq in self.valueset:
            self.fList.append(freq)
            count = sum(1 for v in self.kDict.values() if v == freq)
            self.fDict[freq] = count
        
        print("Sorting List...")
        self.fList.sort()

    def kWrite(self):
        """Write histogram data to output file."""
        with open(f"{self.OutF}.txt", "w") as f:
            f.write("Freq\tNumb\n")
            for freq in self.fList:
                f.write(f"{freq}\t{self.fDict[freq]}\n")


class FastQreader:
    """
    Reads sequences from FastQ format files.
    
    Modified version of FastA reader to handle FastQ format,
    reading every 4th line for sequence data.
    """
    
    def __init__(self, fname: str = ''):
        self.fname = fname

    def doOpen(self):
        """Open input file or use stdin if no filename provided."""
        return sys.stdin if not self.fname else open(self.fname)

    def readFastQ(self) -> Generator[Tuple[str, str], None, None]:
        """
        Read sequences from FastQ file.
        
        Yields:
            Tuple of (header, sequence) for each record
        """
        with self.doOpen() as fileH:
            header = ''
            sequence = ''
            qcount = 2
            
            # Skip to first FastQ header
            line = fileH.readline()
            while not line.startswith('@'):
                if not line:  # EOF
                    return
                line = fileH.readline()
            header = line[1:].rstrip()
            
            # Process file
            for line in fileH:
                if qcount == 1:
                    yield header, sequence
                    header = line[1:].rstrip()
                    sequence = ''
                elif qcount == 2:
                    sequence = ''.join(line.rstrip().split()).upper()
                elif qcount == 4:
                    qcount = 0
                qcount += 1
            
            # Yield final sequence
            yield header, sequence


class CommandLine:
    """Handle command line argument parsing."""
    
    def __init__(self, inOpts=None):
        self.parser = argparse.ArgumentParser(
            description='Generate k-mer frequency histogram from FastQ data',
            epilog='Outputs tab-separated frequency data suitable for plotting',
            prefix_chars='-',
            usage='%(prog)s [options] -option1[default] <input >output'
        )
        
        self.parser.add_argument(
            'inFile',
            action='store',
            help='input FastQ file name'
        )
        self.parser.add_argument(
            'outFile',
            action='store',
            help='output file name (without extension)'
        )
        self.parser.add_argument(
            '-k', '--kmer',
            type=int,
            default=21,
            action='store',
            help='k-mer length (default: 21)'
        )
        
        self.args = self.parser.parse_args(inOpts)


def main(inCL=None):
    """
    Main function to run k-mer analysis.
    
    Args:
        inCL: Optional command line arguments for testing
    """
    # Parse command line arguments
    myCommandLine = CommandLine(inCL)
    
    # Clean up input/output filenames
    output = myCommandLine.args.outFile.replace("outFile=", "").replace("'", "")
    input_file = myCommandLine.args.inFile.replace("inFile=", "").replace("'", "").replace(" ", "")
    kmer_length = myCommandLine.args.kmer
    
    # Display parameters
    print(f"Inputting: {input_file}")
    print(f"Outputting to: {output}.txt")
    print(f"KMer Length: {kmer_length}")
    
    # Run analysis
    myKmer = KmerCount(kmer_length, input_file, output)
    myKmer.addSequence()


if __name__ == "__main__":
    main()