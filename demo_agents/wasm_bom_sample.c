// WU-BOM-001 automatic sandbox demonstration (deliberately incomplete).
// Counts data rows but returns no issues, so hidden tests MUST penalize defects.
// Compile: clang --target=wasm32 -O2 -nostdlib -Wl,--no-entry \
//  -Wl,--export=solve -Wl,--export-memory -Wl,--initial-memory=131072 \
//  -Wl,--max-memory=262144 -Wl,--strip-all demo_agents/wasm_bom_sample.c \
//  -o submission.wasm
// Guest has no WASI, imports, subprocess, network or filesystem.
__attribute__((export_name("solve")))
int solve(int input_offset, int input_size, int output_offset, int output_capacity) {
    if (input_offset < 0 || input_size < 1 || input_size > 65536 ||
        output_offset != 65536 || output_capacity < 27) return -1;
    const volatile unsigned char *in = (const volatile unsigned char *)(unsigned)input_offset;
    unsigned int newlines = 0;
    for (int i=0; i<input_size; ++i) if(in[i]=='\n') ++newlines;
    if (newlines < 1 || newlines > 10) return -1;
    unsigned int rows = newlines - 1;
    volatile unsigned char *out = (volatile unsigned char *)(unsigned)output_offset;
    // {"row_count":0,"issues":[]}, 27 bytes, with a data-derived row count.
    out[0]='{';out[1]='"';out[2]='r';out[3]='o';out[4]='w';out[5]='_';
    out[6]='c';out[7]='o';out[8]='u';out[9]='n';out[10]='t';out[11]='"';
    out[12]=':';out[13]=(unsigned char)('0'+rows);out[14]=',';
    out[15]='"';out[16]='i';out[17]='s';out[18]='s';out[19]='u';
    out[20]='e';out[21]='s';out[22]='"';out[23]=':';out[24]='[';
    out[25]=']';out[26]='}';
    return 27;
}
