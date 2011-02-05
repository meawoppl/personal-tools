# Do Once Function Decorator
# Copyright (c) 2011, Matthew Goodman
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. All advertising materials mentioning features or use of this software
#    must display the following acknowledgement:
#    This product includes software developed by the <organization>.
# 4. Neither the name of the <organization> nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import os, numpy, pickle, hashlib

class DoOnce:
    def __init__(self, dec_f):
        self.f = dec_f
        print "In Init"

    def __call__(self, *args, **kwargs):
        doover = kwargs.pop("do_over", False)
        debug  = kwargs.pop("do_debug", False)

        md5 = hashlib.md5()
            
        # Figure out what we would save it as . . .
        # make a hash on the args and kwargs
        arg_strings  = [str(a) for a in args] 
        arg_strings += [ str(k) + "=" + str(v) for k, v in kwargs.iteritems() ]
        md5.update( ".".join(arg_strings) )
        cache_string = self.f.func_name + "-" + md5.hexdigest()  
        
        # the +4 is for the ".ext"
        if len(cache_string) + 4 >= 254:
            raise RuntimeError("Cache String Too Long")

        # Different file names for numpy arrays and pkls
        pkl_file = os.path.join(".doonce-cache/", cache_string + ".pkl")
        npy_file = os.path.join(".doonce-cache/", cache_string + ".npy")

        # Look for an already computed the result
        # We dont know if it will be a npy or pkl so check both
        if os.path.isfile(pkl_file) and doover == False:
            if debug: print "Previous PKL found:", pkl_file
            return pickle.load(open(pkl_file))
        if os.path.isfile(npy_file) and doover == False:
            if debug: print "Previous NPY found:", npy_file
            return numpy.load(npy_file)
        print "No previous result found, or redoing. . ."

        # I guess we didnt compute the result, or we are recomputing it . . .
        if debug: print "Computing Result . . ."
        res = self.f(*args, **kwargs)
        
        # If it is an ndarray, save it that way, otherwise . . . pickle it!
        if isinstance(res, numpy.ndarray):
            if debug: print "Saving numpy array", npy_file
            flo = open(npy_file, "w")
            numpy.save(flo, res)
        else:
            if debug: print "Saving pickle array", pkl_file
            flo = open(pkl_file, "w")
            pickle.dump(res, flo)
        # Flush and close the file object
        flo.flush()
        flo.close()

        return res
