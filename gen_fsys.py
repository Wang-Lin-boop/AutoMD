import sys
from schrodinger import structure
from schrodinger.infra import mm
from schrodinger.application.desmond.constants import CT_TYPE, TRJ_POINTER, NUM_COMPONENT


def gen_fsys_from_comp(comp_cts):
    """
    This function will assemble full system CT from component CTs.
    """

    full_st = structure.create_new_structure()
    for st in comp_cts:
        full_st = full_st.merge(st, copy_props=True)
    
    full_st.property[CT_TYPE] = CT_TYPE.VAL.FULL_SYSTEM

    # remove ffio_ff block from full_system CT.
    try:
        handle = mm.mmct_ct_m2io_get_unrequested_handle(full_st.handle)
        mm.m2io_delete_named_block(handle, "ffio_ff")
    except mm.MmException:
        pass
        

    return full_st

cts = list(structure.StructureReader(sys.argv[1]))

# clean up
for ct in cts:
    if ct.property.get(CT_TYPE) == CT_TYPE.VAL.FULL_SYSTEM:
        continue
    if ct.property.get(NUM_COMPONENT):
        del ct.property[NUM_COMPONENT]
    if TRJ_POINTER in ct.property:
        del ct.property[TRJ_POINTER]
    if 's_m_original_cms_file' in ct.property:
        del ct.property['s_m_original_cms_file']

fsys_ct = gen_fsys_from_comp(cts)

output_fname = sys.argv[1]
fsys_ct.write(output_fname)
for st in cts:
    st.append(output_fname)
