# -*- coding: UTF-8 -*-
# /*
# *      Copyright (C) 2013 Maros Ondrasek
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */

import json
import urllib2
import math as Math

# http://code.activestate.com/recipes/410692/
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False

class JAKBase64(object):

    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    INDEXED_ALPHABET = ALPHABET
    ASSOCIATED_ALPHABET = dict([(ALPHABET[i],i) for i,j in enumerate(ALPHABET)])

    def atob(self, data):
        output = []
        inpt = "".join(data.split())
        i = 0
        while i<len(inpt):
            enc1 = JAKBase64.ASSOCIATED_ALPHABET[inpt[i]];
            enc2 = JAKBase64.ASSOCIATED_ALPHABET[inpt[i + 1]]
            enc3 = JAKBase64.ASSOCIATED_ALPHABET[inpt[i + 2]]
            enc4 = JAKBase64.ASSOCIATED_ALPHABET[inpt[i + 3]]
            chr1 = (enc1 << 2) | (enc2 >> 4)
            chr2 = ((enc2 & 15) << 4) | (enc3 >> 2)
            chr3 = ((enc3 & 3) << 6) | enc4
            output.append(chr1);
            if (enc3 != 64):
                output.append(chr2)
            if (enc4 != 64):
                output.append(chr3);
            i+=4
        return output;


    def btoa(self, data):
        output = [];
        i = 0;
        ln = len(data)
        while True:
            if (i < len(data)): chr1 = data[i]; i+=1
            else: chr1='NaN'
            if (i < len(data)): chr2 = data[i]; i+=1
            else: chr2='NaN'
            if (i < len(data)): chr3 = data[i]; i+=1
            else: chr3='NaN'
            enc1 = chr1 >> 2 if chr1 !='NaN' else 0

            if chr1 == 'NaN' or chr2 == 'NaN':
                if chr1 == 'NaN' and chr2 == 'NaN':
                    enc2 = 0
                elif chr1 == 'NaN':
                    enc2 = 0|(chr2 >> 4)
                elif chr2 == 'NaN':
                    enc2 =  ((chr1 & 3) << 4)|0
            else:
                enc2 = ((chr1 & 3) << 4) | (chr2 >> 4)

            if chr2 == 'NaN' or chr3 == 'NaN':
                if chr2 == 'NaN' and chr3 == 'NaN':
                    enc3 = 0
                elif chr2 == 'NaN':
                    enc3 = 0|(chr3 >> 6)
                elif chr3 == 'NaN':
                    enc3 =  ((chr2 & 15) << 2)|0
            else:
                enc3 = ((chr2 & 15) << 2) | (chr3 >> 6)

            enc4 = chr3 & 63 if chr3 !='NaN' else 0;
            if (chr2 == 'NaN'):
                enc3 = enc4 = 64;
            else:
                if (chr3 == 'NaN'):
                    enc4 = 64
            output.append(JAKBase64.INDEXED_ALPHABET[enc1]);
            output.append(JAKBase64.INDEXED_ALPHABET[enc2]);
            output.append(JAKBase64.INDEXED_ALPHABET[enc3]);
            output.append(JAKBase64.INDEXED_ALPHABET[enc4]);
            if (i>=ln):
                break
        return "".join(output)



class JAKFRPC(object):

    TYPE_MAGIC = 25;
    TYPE_CALL = 13;
    TYPE_RESPONSE = 14;
    TYPE_FAULT = 15;
    TYPE_INT = 1;
    TYPE_BOOL = 2;
    TYPE_DOUBLE = 3;
    TYPE_STRING = 4;
    TYPE_DATETIME = 5;
    TYPE_BINARY = 6;
    TYPE_INT8P = 7;
    TYPE_INT8N = 8;
    TYPE_STRUCT = 10;
    TYPE_ARRAY = 11;
    TYPE_None = 12;

    def __init__(self):
        self._hints = None
        self._path = []
        self._hints = None
        self._path = [];
        self._data = [];
        self._pointer = 0;

    def parse(self, data):
        self._pointer = 0;
        self._data = data;
        magic = self._getBytes(4);
        if (magic[0] != 202 or magic[1] != 17):
            self._data = [];
            raise Exception("Missing FRPC magic")

        first = self._getInt(1);
        tpe = first >> 3;
        if (tpe == JAKFRPC.TYPE_FAULT):
            num = self._parseValue()
            msg = self._parseValue()
            self._data = [];
            raise Exception("FRPC/" + num + ": " + msg);

        result = None;
        for case in switch (tpe):
            if case(JAKFRPC.TYPE_RESPONSE):
                result = self._parseValue()
                if (self._pointer < len(self._data)):
                    self._data = []
                    raise Exception("Garbage after FRPC data");
                break
            if case(JAKFRPC.TYPE_CALL):
                nameLength = self._getInt(1);
                name = self._decodeUTF8(nameLength);
                params = []
                while (self._pointer < self._data.length):
                    params.append(self._parseValue());

                self._data = []
                return {
                "method": name,
                "params": params
                }
                break
            if case():
                self._data = [];
                raise Exception("Unsupported FRPC type " + tpe)
                break

        self._data = []
        return result

    def serializeCall(self,method, data, hints=None):
        result = self.serialize(data, hints)
        result.pop(0)
        result.pop(0)
        encodedMethod = self._encodeUTF8(method);
        result=encodedMethod + result
        result=[len(encodedMethod)] + result
        result=[(JAKFRPC.TYPE_CALL << 3)] + result
        result=[202,17,2,0] + result
        return result

    def serialize(self, data, hints):
        result = []
        self._hints = hints
        self._serializeValue(result, data)
        self._hints = None
        return result

    def _parseValue(self):
        first = self._getInt(1);
        type = first >> 3;
        for case in switch(type):
            if case(JAKFRPC.TYPE_STRUCT):
                result = {}
                lengthBytes = (first & 7) + 1;
                members = self._getInt(lengthBytes);
                while (members):
                    self._parseMember(result);
                    members-=1
                return result
                break
            if case (JAKFRPC.TYPE_ARRAY):
                result = []
                lengthBytes = (first & 7) + 1
                members = self._getInt(lengthBytes);
                while (members):
                    result.append(self._parseValue());
                    members-=1
                return result
                break
            if case(JAKFRPC.TYPE_BOOL):
                return (first & 1) # VERIFY
                break;
            if case(JAKFRPC.TYPE_STRING):
                lengthBytes = (first & 7) + 1;
                length = self._getInt(lengthBytes);
                return self._decodeUTF8(length);
                break;
            if case(JAKFRPC.TYPE_INT8P):
                length = (first & 7) + 1;
                return self._getInt(length);
                break
            if case(JAKFRPC.TYPE_INT8N):
                length = (first & 7) + 1;
                return -self._getInt(length);
                break;
            if case(JAKFRPC.TYPE_INT):
                length = first & 7;
                max = Math.pow(2, 8 * length);
                result = self._getInt(length);
                if (result >= max / 2):
                    result -= max
                return result;
                break;
            if case(JAKFRPC.TYPE_DOUBLE):
                return self._getDouble();
                break;
            if case(JAKFRPC.TYPE_DATETIME):
                self._getBytes(1);
                ts = self._getInt(4);
                self._getBytes(5);
                return ""#new Date(1000 * ts); TODO
                break;
            if case(JAKFRPC.TYPE_BINARY):
                lengthBytes = (first & 7) + 1;
                length = self._getInt(lengthBytes);
                return self._getBytes(length);
                break;
            if case(JAKFRPC.TYPE_None):
                return None;
                break;
            if case():
                raise Exception("Unkown FRPC type " + type);
                break

    def _append(self,arr1, arr2):
        arr1.extend(arr2)

    def _parseMember(self, result):
        nameLength = self._getInt(1);
        name = self._decodeUTF8(nameLength);
        result[name] = self._parseValue();

    def _getInt(self, bytes):
        buffer = self._getBytes(bytes);
        result = 0;
        factor = 1;
        while (len(buffer)):
            result += factor * buffer.pop(0);
            factor *= 256
        return result;

    def _getBytes(self, count):
        if ((self._pointer + count) > len(self._data)):
            raise Exception("Cannot read " + count + " bytes from buffer");
        result = self._data[self._pointer: self._pointer + count]
        self._pointer += count
        return result

    def _decodeUTF8(self, length):
        buffer = self._getBytes(length);
        result = [];
        i = 0;
        c = c1 = c2 = 0
        while (i < len(buffer)):
            c = buffer[i];
            if (c < 128):
                result.append(unichr(c));
                i+=1
            else:
                if ((c > 191) and (c < 224)):
                    c2 = buffer[i + 1];
                    result.append(unichr(((c & 31) << 6) | (c2 & 63)));
                    i += 2;
                else:
                    c2 = buffer[i + 1];
                    c3 = buffer[i + 2];
                    result.append(unichr(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63)));
                    i += 3
        return "".join(result)

    def _encodeUTF8(self, st):
        result = []
        i = 0
        while i < len(st):
            c = ord(st[i])
            if (c < 128):
                result.append(c)
            else:
                if ((c > 127) and (c < 2048)):
                    result.append((c >> 6) | 192)
                    result.append((c & 63) | 128)
                else:
                    result.append((c >> 12) | 224)
                    result.append(((c >> 6) & 63) | 128)
                    result.append((c & 63) | 128)
            i+=1
        return result

    def _getDouble(self):
        bytes = self._getBytes(8)[::-1]
        sign = 1 if (bytes[0] & 128) else 0
        exponent = (bytes[0] & 127) << 4;
        exponent += bytes[1] >> 4;
        if (exponent == 0):
            return Math.pow(-1, sign) * 0;
        mantissa = 0;
        byteIndex = 1;
        bitIndex = 3;
        index = 1;
        while True:
            bitValue = 1 if (bytes[byteIndex] & (1 << bitIndex)) else 0
            mantissa += bitValue * Math.pow(2, -index);
            index+=1
            bitIndex-=1;
            if (bitIndex < 0):
                bitIndex = 7;
                byteIndex+=1;
            if byteIndex >= len(bytes):
                break
        if (exponent == 2047):
            if (mantissa):
                return NaN;
            else:
                return Math.pow(-1, sign) * Infinity;

        exponent -= (1 << 10) - 1
        return Math.pow(-1, sign) * Math.pow(2, exponent) * (1 + mantissa)

    def _serializeValue(self, result, value):
        if (value is None):
            result.append(JAKFRPC.TYPE_None << 3)
            return

        for case in switch(value.__class__.__name__):
            if case("str"):
                strData = self._encodeUTF8(value)
                intData = self._encodeInt(len(strData))
                first = JAKFRPC.TYPE_STRING << 3
                first += (len(intData) - 1)
                result.append(first)
                self._append(result, intData)
                self._append(result, strData)
                break
            if case("int"):
                if (self._getHint() == "float"):
                    first = JAKFRPC.TYPE_DOUBLE << 3;
                    floatData = self._encodeDouble(value);
                    result.append(first);
                    self._append(result, floatData);
                else:
                    first = JAKFRPC.TYPE_INT8P  if (value > 0) else JAKFRPC.TYPE_INT8N
                    first = first << 3;
                    data = self._encodeInt(Math.fabs(value));
                    first += (len(data) - 1)
                    result.append(first);
                    self._append(result, data);
                break;
            if case("bool"):
                data = JAKFRPC.TYPE_BOOL << 3;
                if (value):
                    data += 1;
                result.append(data)
                break;
            if case("list"):
                # missing date and struct for now
                self._serializeArray(result, value);
                break
            if case():
                raise Exception("FRPC does not allow value " + str(type(value).__name__))
                break

    def _serializeArray(self, result, data):
        if (self._getHint() == "binary"):
            first = self.FRPC.TYPE_BINARY << 3;
            intData = self._encodeInt(len(data))
            first += (len(intData) - 1)
            result.append(first)
            self._append(result, intData);
            self._append(result, data);
            return;

        first = JAKFRPC.TYPE_ARRAY << 3;
        intData = self._encodeInt(len(data));
        first += (len(intData) - 1);
        result.append(first);
        self._append(result, intData)
        i = 0
        while i<len(data):
            self._path.append(i);
            self._serializeValue(result, data[i]);
            self._path.pop();
            i+=1

    def _serializeStruct(self, result, data):
        raise Exception("serializeStruct unsupported")

    def _serializeDate(self,result, date):
        raise Exception("serializeDate unsupported")

    def _encodeInt(self, data):
        if  (not data):
            return [0]
        result = []
        remain = data
        while (remain):
            value = remain % 256;
            remain = (remain - value) / 256;
            result.append(int(value));
        return result;

    def _encodeDouble(self, num):
        raise Exception("encodeDouble unsupported")

    def _getHint(self):
        if (not self._hints):
            return None
        if (type (self._hints) != "object"):
            return self._hints;
        return self._hints[".".join(self._path)] or None


def sendRPC(requestMethod, params):
    frpc = JAKFRPC()
    b64 = JAKBase64()
    data= b64.btoa(frpc.serializeCall(requestMethod, [params]))
    headers = {'Accept':'application/json',
                      'Content-Type':'application/x-base64-frpc; charset=UTF-8',
                      'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0'}
    req = urllib2.Request('http://www.mixer.cz/RPC2/',data,headers)
    resp = urllib2.urlopen(req)
    data = json.load(resp)
    resp.close()
    if data['status'] != 200:
        raise Exception(data['statusMessage'])
    return data
