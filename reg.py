import sys
import getopt
import gzip
from classes import ConData, file_to_con_data, Reg

def reg(argv):
    # default parameters
    use_presets = False
    inc_regs = []
    exc_regs = []
    
    # presets
    presets = {
        "hm":[Reg(str(i + 1)) for i in range(22)] + [Reg("X"), Reg("Y")],
        "hf":[Reg(str(i + 1)) for i in range(22)] + [Reg("X")],
        "mm":[Reg("chr" + str(i + 1)) for i in range(19)] + [Reg("chrX"), Reg("chrY")],
        "mf":[Reg("chr" + str(i + 1)) for i in range(19)] + [Reg("chrX")]}
    preset_descriptions = {
        "hm":"human male (no \"chr\" prefix)",
        "hf":"human female (no \"chr\" prefix)",
        "mm":"mouse male",
        "mf":"mouse female"}
    
    # progress display parameters
    max_num_dups = 10
    
    # read arguments
    try:
        opts, args = getopt.getopt(argv[1:], "i:e:p:")
    except getopt.GetoptError as err:
        sys.stderr.write("[E::" + __name__ + "] unknown command\n")
        return 1
    if len(args) == 0:
        sys.stderr.write("Usage: metac reg [options] <in.con>\n")
        sys.stderr.write("Options:\n")
        sys.stderr.write("  -i <inc.reg>   the only regions to include:\n")
        sys.stderr.write("                   tab-delimited: chr, haplotype, start, end\n")
        sys.stderr.write("                   haplotype: 0 = paternal, 1 = maternal, . = both\n")
        sys.stderr.write("                   start/end: . = denotes end of chromosome\n")
        sys.stderr.write("  -e <exc.reg>   regions to exclude (same format as above)\n")
        sys.stderr.write("  -p STR         presets for included regions:\n")
        for preset in sorted(presets.keys()):
            sys.stderr.write("                   " + preset + " = " + preset_descriptions[preset] + "\n")
        return 1
    for o, a in opts:
        if o == "-p":
            try:
                inc_regs = presets[a]
                sys.stderr.write("[M::" + __name__ + "] use preset " + a + " = " + preset_descriptions[a] + "\n")
            except KeyError:
                sys.stderr.write("[E::" + __name__ + "] unknown preset\n")
                return 1
            use_presets = True
        elif o == "-i":
            use_presets = False
        elif o == "-e":
            use_presets = False  
                     
    # display regions
    sys.stderr.write("[M::" + __name__ + "] only include the following regions:\n")
    sys.stderr.write("chr\thap\tstart\tend\n")
    for reg in inc_regs:
        sys.stderr.write(reg.to_string() + "\n")
    sys.stderr.write("[M::" + __name__ + "] only exclude the following regions:\n")
    sys.stderr.write("chr\thap\tstart\tend\n")
    for reg in exc_regs:
        sys.stderr.write(reg.to_string() + "\n")
    
    # read CON file
    con_file = gzip.open(args[0], "rb") if args[0].endswith(".gz") else open(args[0], "rb")
    con_data = file_to_con_data(con_file)
    sys.stderr.write("[M::" + __name__ + "] read " + str(con_data.num_cons()) + " putative contacts (" +  str(round(100.0 * con_data.num_phased_legs() / con_data.num_cons() / 2, 2)) + "% legs phased)\n")
    con_data.apply_regs(inc_regs, exc_regs)
    sys.stderr.write("[M::" + __name__ + "] writing output for " + str(con_data.num_cons()) + " putative contacts (" + str(round(100.0 * con_data.num_intra_chr() / con_data.num_cons(), 2)) + "% intra-chromosomal, " + str(round(100.0 * con_data.num_phased_legs() / con_data.num_cons() / 2, 2)) + "% legs phased)\n")
    sys.stdout.write(con_data.to_string()+"\n")
    
        
    return 0
    