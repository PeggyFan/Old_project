
import re
from nltk.compat import python_2_unicode_compatible
from nltk.corpus.reader import CorpusReader

@python_2_unicode_compatible
class SentiWordNetCorpusReader(CorpusReader):
    def __init__(self, root, fileids, encoding='utf-8'):
        """
        Construct a new SentiWordNet Corpus Reader, using data from
    the specified file.
        """        
        super(SentiWordNetCorpusReader, self).__init__(root, fileids,
                                                  encoding=encoding)
        if len(self._fileids) != 1:
            raise ValueError('Exactly one file must be specified')
        self._db = {}
        self._parse_src_file()

    def _parse_src_file(self):
        lines = self.open(self._fileids[0]).read().splitlines()
        lines = filter((lambda x : not re.search(r"^\s*#", x)), lines)
        for i, line in enumerate(lines):
            fields = [field.strip() for field in re.split(r"\t+", line)]
            try:            
                pos, offset, pos_score, neg_score, synset_terms, gloss = fields
            except:
                raise ValueError('Line %s formatted incorrectly: %s\n' % (i, line))
            if pos and offset:
                offset = int(offset)
                self._db[(pos, offset)] = (float(pos_score), float(neg_score))

    def senti_synset(self, *vals):        
        from nltk.corpus import wordnet as wn
        if tuple(vals) in self._db:
            pos_score, neg_score = self._db[tuple(vals)]
            pos, offset = vals
            synset = wn._synset_from_pos_and_offset(pos, offset)
            return SentiSynset(pos_score, neg_score, synset)
        else:
            synset = wn.synset(vals[0])
            pos = synset.pos()
            offset = synset.offset()
            if (pos, offset) in self._db:
                pos_score, neg_score = self._db[(pos, offset)]
                return SentiSynset(pos_score, neg_score, synset)
            else:
                return None

    def senti_synsets(self, string, pos=None):
        from nltk.corpus import wordnet as wn
        sentis = []
        synset_list = wn.synsets(string, pos)
        for synset in synset_list:
            sentis.append(self.senti_synset(synset.name()))
        sentis = filter(lambda x : x, sentis)
        return sentis

    def all_senti_synsets(self):
        from nltk.corpus import wordnet as wn
        for key, fields in self._db.items():
            pos, offset = key
            pos_score, neg_score = fields
            synset = wn._synset_from_pos_and_offset(pos, offset)
            yield SentiSynset(pos_score, neg_score, synset)


@python_2_unicode_compatible
class SentiSynset(object):
    def __init__(self, pos_score, neg_score, synset):
        self._pos_score = pos_score
        self._neg_score = neg_score
        self._obj_score = 1.0 - (self._pos_score + self._neg_score)
        self.synset = synset

    def pos_score(self):
        return self._pos_score

    def neg_score(self):
        return self._neg_score

    def obj_score(self):
        return self._obj_score

    def __str__(self):
        """Prints just the Pos/Neg scores for now."""
        s = "<"
        s += self.synset.name() + ": "
        s += "PosScore=%s " % self._pos_score
        s += "NegScore=%s" % self._neg_score
        s += ">"
        return s

    def __repr__(self):
        return "Senti" + repr(self.synset)
                    