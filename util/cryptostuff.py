

from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import MD5



r_gen = Random.new().read
key = RSA.generate(1024, r_gen)
pubkey = key.publickey()

with open('id_pub.rsa','w') as ofile:
    ofile.write(pubkey.exportKey())
import ipdb; ipdb.set_trace()
edata = pubkey.encrypt('a string with a message in it', None)
mh = MD5.new('tinyco').hexdigest()

print mh
signed = key.sign(mh, edata)

print pubkey.verify(mh, signed)
print key.decrypt(edata)

#~ signed
#~ edata
#~ print edata[0]
#~ int(signed[0], 16)
#~ int(str(signed[0]), 16)
#~ import struct
#~ struct.pack
#~ struct.pack ??
#~ struct.pack ?
#~ ? struct.pack
#~ help(struct.pack)
#~ struct.pack('d', signed[0])
#~ struct.pack('dd', signed[0])
#~ struct.pack('d', signed[0])
#~ struct.unpack('d', '\xee\xfa\xf5\x88)\x96\xe1\x7f')
#~ print _[0]
#~ signed[0]
#~ __
#~ mr = _[0]
#~ mr
#~ signed[0] == mr
#~ signed[0]- mr
 #~ mr - signed[0]
#~ mr += 1
#~ signed[0]- mr
 #~ mr - signed[0]
#~ struct.pack('ll', signed[0])
#~ struct.pack('l', signed[0])
#~ struct.pack('q', signed[0])
#~ signed[0]
#~ str(signed[0]_
#~ )
#~ str(signed[0])
#~ len(str(signed[0]))
#~ struct.pack('b'*len(str(signed[0])), *str(signed[0]))
#~ struct.pack('b'*len(str(signed[0])), str(signed[0]))
#~ struct.pack('b', str(signed[0]))
#~ struct.pack('b', signed[0])
#~ struct.pack('b', signed[0])
