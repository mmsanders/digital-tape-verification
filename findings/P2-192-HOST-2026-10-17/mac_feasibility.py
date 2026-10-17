"""Synthetic information-loss controls, not a native capture or replacement method."""
import hashlib,json

CAPACITY=4296015872
HIGH=CAPACITY-512
LOW=HIGH%(2**32)
pattern=hashlib.sha256(b'Verification192 unique mirror pattern').digest()*16
wrong=hashlib.sha256(b'wrong mirror').digest()*16

def fs_observation(offset,n):
    # The already-established fs_usage limitation: upper bits and payload absent.
    return {'offset_low32':offset%(2**32),'native_returned_length':n,'status':0}

def conditional_payload(data,n):
    # This would require a real native returned-buffer observation, which the
    # current SIP-on method does NOT supply. It proves content, not high bits.
    return 'PASS_CONTENT_ONLY' if n==512 and len(data)==512 and data==pattern else 'REJECT'

def run():
    good=fs_observation(HIGH,512);alias=fs_observation(LOW,512)
    assert HIGH!=LOW and good==alias
    assert conditional_payload(pattern,512)=='PASS_CONTENT_ONLY'
    assert conditional_payload(wrong,512)=='REJECT'
    assert conditional_payload(pattern[:511],511)=='REJECT'
    assert conditional_payload(pattern,511)=='REJECT'
    # Change the actual native address while holding returned content constant.
    # A content-only rule cannot reject this wrong-address world.
    correct_world={'actual_offset':HIGH,'returned_bytes':pattern,'returned_length':512}
    wrong_address_world={'actual_offset':LOW,'returned_bytes':pattern,'returned_length':512}
    assert correct_world['actual_offset']!=wrong_address_world['actual_offset']
    assert all(conditional_payload(w['returned_bytes'],w['returned_length'])=='PASS_CONTENT_ONLY' for w in (correct_world,wrong_address_world))
    return {'kind':'SYNTHETIC feasibility/causal controls only','high':HIGH,'alias':LOW,'observations_equal':good==alias,'current_method_verdict':'HELD: cannot distinguish native high address from low alias','conditional_correct_pattern':'PASS_CONTENT_ONLY','conditional_wrong_mirror':'REJECT','conditional_short_read':'REJECT','conditional_low_alias_with_same_content':'PASS_CONTENT_ONLY; native address still HELD','native_returned_buffer_available_in_existing_SIP_on_method':False,'method_issued':False}

if __name__=='__main__':print(json.dumps(run(),indent=2))
