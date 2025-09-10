/*
 * This script contains the language-specific data used by searchtools.js,
 * namely the list of stopwords, stemmer, scorer and splitter.
 */

var stopwords = ["ai", "aie", "aient", "aies", "ait", "as", "au", "aura", "aurai", "auraient", "aurais", "aurait", "auras", "aurez", "auriez", "aurions", "aurons", "auront", "aux", "avaient", "avais", "avait", "avec", "avez", "aviez", "avions", "avons", "ayant", "ayez", "ayons", "c", "ce", "ceci", "cela", "cel\u00e0", "ces", "cet", "cette", "d", "dans", "de", "des", "du", "elle", "en", "es", "est", "et", "eu", "eue", "eues", "eurent", "eus", "eusse", "eussent", "eusses", "eussiez", "eussions", "eut", "eux", "e\u00fbmes", "e\u00fbt", "e\u00fbtes", "furent", "fus", "fusse", "fussent", "fusses", "fussiez", "fussions", "fut", "f\u00fbmes", "f\u00fbt", "f\u00fbtes", "ici", "il", "ils", "j", "je", "l", "la", "le", "les", "leur", "leurs", "lui", "m", "ma", "mais", "me", "mes", "moi", "mon", "m\u00eame", "n", "ne", "nos", "notre", "nous", "on", "ont", "ou", "par", "pas", "pour", "qu", "que", "quel", "quelle", "quelles", "quels", "qui", "s", "sa", "sans", "se", "sera", "serai", "seraient", "serais", "serait", "seras", "serez", "seriez", "serions", "serons", "seront", "ses", "soi", "soient", "sois", "soit", "sommes", "son", "sont", "soyez", "soyons", "suis", "sur", "t", "ta", "te", "tes", "toi", "ton", "tu", "un", "une", "vos", "votre", "vous", "y", "\u00e0", "\u00e9taient", "\u00e9tais", "\u00e9tait", "\u00e9tant", "\u00e9tiez", "\u00e9tions", "\u00e9t\u00e9", "\u00e9t\u00e9e", "\u00e9t\u00e9es", "\u00e9t\u00e9s", "\u00eates"];


/* Non-minified version is copied as a separate JS file, if available */
/**@constructor*/
BaseStemmer = function() {
    this.setCurrent = function(value) {
        this.current = value;
        this.cursor = 0;
        this.limit = this.current.length;
        this.limit_backward = 0;
        this.bra = this.cursor;
        this.ket = this.limit;
    };

    this.getCurrent = function() {
        return this.current;
    };

    this.copy_from = function(other) {
        this.current          = other.current;
        this.cursor           = other.cursor;
        this.limit            = other.limit;
        this.limit_backward   = other.limit_backward;
        this.bra              = other.bra;
        this.ket              = other.ket;
    };

    this.in_grouping = function(s, min, max) {
        if (this.cursor >= this.limit) return false;
        var ch = this.current.charCodeAt(this.cursor);
        if (ch > max || ch < min) return false;
        ch -= min;
        if ((s[ch >>> 3] & (0x1 << (ch & 0x7))) == 0) return false;
        this.cursor++;
        return true;
    };

    this.in_grouping_b = function(s, min, max) {
        if (this.cursor <= this.limit_backward) return false;
        var ch = this.current.charCodeAt(this.cursor - 1);
        if (ch > max || ch < min) return false;
        ch -= min;
        if ((s[ch >>> 3] & (0x1 << (ch & 0x7))) == 0) return false;
        this.cursor--;
        return true;
    };

    this.out_grouping = function(s, min, max) {
        if (this.cursor >= this.limit) return false;
        var ch = this.current.charCodeAt(this.cursor);
        if (ch > max || ch < min) {
            this.cursor++;
            return true;
        }
        ch -= min;
        if ((s[ch >>> 3] & (0X1 << (ch & 0x7))) == 0) {
            this.cursor++;
            return true;
        }
        return false;
    };

    this.out_grouping_b = function(s, min, max) {
        if (this.cursor <= this.limit_backward) return false;
        var ch = this.current.charCodeAt(this.cursor - 1);
        if (ch > max || ch < min) {
            this.cursor--;
            return true;
        }
        ch -= min;
        if ((s[ch >>> 3] & (0x1 << (ch & 0x7))) == 0) {
            this.cursor--;
            return true;
        }
        return false;
    };

    this.eq_s = function(s)
    {
        if (this.limit - this.cursor < s.length) return false;
        if (this.current.slice(this.cursor, this.cursor + s.length) != s)
        {
            return false;
        }
        this.cursor += s.length;
        return true;
    };

    this.eq_s_b = function(s)
    {
        if (this.cursor - this.limit_backward < s.length) return false;
        if (this.current.slice(this.cursor - s.length, this.cursor) != s)
        {
            return false;
        }
        this.cursor -= s.length;
        return true;
    };

    /** @return {number} */ this.find_among = function(v)
    {
        var i = 0;
        var j = v.length;

        var c = this.cursor;
        var l = this.limit;

        var common_i = 0;
        var common_j = 0;

        var first_key_inspected = false;

        while (true)
        {
            var k = i + ((j - i) >>> 1);
            var diff = 0;
            var common = common_i < common_j ? common_i : common_j; // smaller
            // w[0]: string, w[1]: substring_i, w[2]: result, w[3]: function (optional)
            var w = v[k];
            var i2;
            for (i2 = common; i2 < w[0].length; i2++)
            {
                if (c + common == l)
                {
                    diff = -1;
                    break;
                }
                diff = this.current.charCodeAt(c + common) - w[0].charCodeAt(i2);
                if (diff != 0) break;
                common++;
            }
            if (diff < 0)
            {
                j = k;
                common_j = common;
            }
            else
            {
                i = k;
                common_i = common;
            }
            if (j - i <= 1)
            {
                if (i > 0) break; // v->s has been inspected
                if (j == i) break; // only one item in v

                // - but now we need to go round once more to get
                // v->s inspected. This looks messy, but is actually
                // the optimal approach.

                if (first_key_inspected) break;
                first_key_inspected = true;
            }
        }
        do {
            var w = v[i];
            if (common_i >= w[0].length)
            {
                this.cursor = c + w[0].length;
                if (w.length < 4) return w[2];
                var res = w[3](this);
                this.cursor = c + w[0].length;
                if (res) return w[2];
            }
            i = w[1];
        } while (i >= 0);
        return 0;
    };

    // find_among_b is for backwards processing. Same comments apply
    this.find_among_b = function(v)
    {
        var i = 0;
        var j = v.length

        var c = this.cursor;
        var lb = this.limit_backward;

        var common_i = 0;
        var common_j = 0;

        var first_key_inspected = false;

        while (true)
        {
            var k = i + ((j - i) >> 1);
            var diff = 0;
            var common = common_i < common_j ? common_i : common_j;
            var w = v[k];
            var i2;
            for (i2 = w[0].length - 1 - common; i2 >= 0; i2--)
            {
                if (c - common == lb)
                {
                    diff = -1;
                    break;
                }
                diff = this.current.charCodeAt(c - 1 - common) - w[0].charCodeAt(i2);
                if (diff != 0) break;
                common++;
            }
            if (diff < 0)
            {
                j = k;
                common_j = common;
            }
            else
            {
                i = k;
                common_i = common;
            }
            if (j - i <= 1)
            {
                if (i > 0) break;
                if (j == i) break;
                if (first_key_inspected) break;
                first_key_inspected = true;
            }
        }
        do {
            var w = v[i];
            if (common_i >= w[0].length)
            {
                this.cursor = c - w[0].length;
                if (w.length < 4) return w[2];
                var res = w[3](this);
                this.cursor = c - w[0].length;
                if (res) return w[2];
            }
            i = w[1];
        } while (i >= 0);
        return 0;
    };

    /* to replace chars between c_bra and c_ket in this.current by the
     * chars in s.
     */
    this.replace_s = function(c_bra, c_ket, s)
    {
        var adjustment = s.length - (c_ket - c_bra);
        this.current = this.current.slice(0, c_bra) + s + this.current.slice(c_ket);
        this.limit += adjustment;
        if (this.cursor >= c_ket) this.cursor += adjustment;
        else if (this.cursor > c_bra) this.cursor = c_bra;
        return adjustment;
    };

    this.slice_check = function()
    {
        if (this.bra < 0 ||
            this.bra > this.ket ||
            this.ket > this.limit ||
            this.limit > this.current.length)
        {
            return false;
        }
        return true;
    };

    this.slice_from = function(s)
    {
        var result = false;
        if (this.slice_check())
        {
            this.replace_s(this.bra, this.ket, s);
            result = true;
        }
        return result;
    };

    this.slice_del = function()
    {
        return this.slice_from("");
    };

    this.insert = function(c_bra, c_ket, s)
    {
        var adjustment = this.replace_s(c_bra, c_ket, s);
        if (c_bra <= this.bra) this.bra += adjustment;
        if (c_bra <= this.ket) this.ket += adjustment;
    };

    this.slice_to = function()
    {
        var result = '';
        if (this.slice_check())
        {
            result = this.current.slice(this.bra, this.ket);
        }
        return result;
    };

    this.assign_to = function()
    {
        return this.current.slice(0, this.limit);
    };
};

// Generated by Snowball 2.1.0 - https://snowballstem.org/

/**@constructor*/
FrenchStemmer = function() {
    var base = new BaseStemmer();
    /** @const */ var a_0 = [
        ["col", -1, -1],
        ["par", -1, -1],
        ["tap", -1, -1]
    ];

    /** @const */ var a_1 = [
        ["", -1, 7],
        ["H", 0, 6],
        ["He", 1, 4],
        ["Hi", 1, 5],
        ["I", 0, 1],
        ["U", 0, 2],
        ["Y", 0, 3]
    ];

    /** @const */ var a_2 = [
        ["iqU", -1, 3],
        ["abl", -1, 3],
        ["I\u00E8r", -1, 4],
        ["i\u00E8r", -1, 4],
        ["eus", -1, 2],
        ["iv", -1, 1]
    ];

    /** @const */ var a_3 = [
        ["ic", -1, 2],
        ["abil", -1, 1],
        ["iv", -1, 3]
    ];

    /** @const */ var a_4 = [
        ["iqUe", -1, 1],
        ["atrice", -1, 2],
        ["ance", -1, 1],
        ["ence", -1, 5],
        ["logie", -1, 3],
        ["able", -1, 1],
        ["isme", -1, 1],
        ["euse", -1, 11],
        ["iste", -1, 1],
        ["ive", -1, 8],
        ["if", -1, 8],
        ["usion", -1, 4],
        ["ation", -1, 2],
        ["ution", -1, 4],
        ["ateur", -1, 2],
        ["iqUes", -1, 1],
        ["atrices", -1, 2],
        ["ances", -1, 1],
        ["ences", -1, 5],
        ["logies", -1, 3],
        ["ables", -1, 1],
        ["ismes", -1, 1],
        ["euses", -1, 11],
        ["istes", -1, 1],
        ["ives", -1, 8],
        ["ifs", -1, 8],
        ["usions", -1, 4],
        ["ations", -1, 2],
        ["utions", -1, 4],
        ["ateurs", -1, 2],
        ["ments", -1, 15],
        ["ements", 30, 6],
        ["issements", 31, 12],
        ["it\u00E9s", -1, 7],
        ["ment", -1, 15],
        ["ement", 34, 6],
        ["issement", 35, 12],
        ["amment", 34, 13],
        ["emment", 34, 14],
        ["aux", -1, 10],
        ["eaux", 39, 9],
        ["eux", -1, 1],
        ["it\u00E9", -1, 7]
    ];

    /** @const */ var a_5 = [
        ["ira", -1, 1],
        ["ie", -1, 1],
        ["isse", -1, 1],
        ["issante", -1, 1],
        ["i", -1, 1],
        ["irai", 4, 1],
        ["ir", -1, 1],
        ["iras", -1, 1],
        ["ies", -1, 1],
        ["\u00EEmes", -1, 1],
        ["isses", -1, 1],
        ["issantes", -1, 1],
        ["\u00EEtes", -1, 1],
        ["is", -1, 1],
        ["irais", 13, 1],
        ["issais", 13, 1],
        ["irions", -1, 1],
        ["issions", -1, 1],
        ["irons", -1, 1],
        ["issons", -1, 1],
        ["issants", -1, 1],
        ["it", -1, 1],
        ["irait", 21, 1],
        ["issait", 21, 1],
        ["issant", -1, 1],
        ["iraIent", -1, 1],
        ["issaIent", -1, 1],
        ["irent", -1, 1],
        ["issent", -1, 1],
        ["iront", -1, 1],
        ["\u00EEt", -1, 1],
        ["iriez", -1, 1],
        ["issiez", -1, 1],
        ["irez", -1, 1],
        ["issez", -1, 1]
    ];

    /** @const */ var a_6 = [
        ["a", -1, 3],
        ["era", 0, 2],
        ["asse", -1, 3],
        ["ante", -1, 3],
        ["\u00E9e", -1, 2],
        ["ai", -1, 3],
        ["erai", 5, 2],
        ["er", -1, 2],
        ["as", -1, 3],
        ["eras", 8, 2],
        ["\u00E2mes", -1, 3],
        ["asses", -1, 3],
        ["antes", -1, 3],
        ["\u00E2tes", -1, 3],
        ["\u00E9es", -1, 2],
        ["ais", -1, 3],
        ["erais", 15, 2],
        ["ions", -1, 1],
        ["erions", 17, 2],
        ["assions", 17, 3],
        ["erons", -1, 2],
        ["ants", -1, 3],
        ["\u00E9s", -1, 2],
        ["ait", -1, 3],
        ["erait", 23, 2],
        ["ant", -1, 3],
        ["aIent", -1, 3],
        ["eraIent", 26, 2],
        ["\u00E8rent", -1, 2],
        ["assent", -1, 3],
        ["eront", -1, 2],
        ["\u00E2t", -1, 3],
        ["ez", -1, 2],
        ["iez", 32, 2],
        ["eriez", 33, 2],
        ["assiez", 33, 3],
        ["erez", 32, 2],
        ["\u00E9", -1, 2]
    ];

    /** @const */ var a_7 = [
        ["e", -1, 3],
        ["I\u00E8re", 0, 2],
        ["i\u00E8re", 0, 2],
        ["ion", -1, 1],
        ["Ier", -1, 2],
        ["ier", -1, 2]
    ];

    /** @const */ var a_8 = [
        ["ell", -1, -1],
        ["eill", -1, -1],
        ["enn", -1, -1],
        ["onn", -1, -1],
        ["ett", -1, -1]
    ];

    /** @const */ var /** Array<int> */ g_v = [17, 65, 16, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 130, 103, 8, 5];

    /** @const */ var /** Array<int> */ g_keep_with_s = [1, 65, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128];

    var /** number */ I_p2 = 0;
    var /** number */ I_p1 = 0;
    var /** number */ I_pV = 0;


    /** @return {boolean} */
    function r_prelude() {
        while(true)
        {
            var /** number */ v_1 = base.cursor;
            lab0: {
                golab1: while(true)
                {
                    var /** number */ v_2 = base.cursor;
                    lab2: {
                        lab3: {
                            var /** number */ v_3 = base.cursor;
                            lab4: {
                                if (!(base.in_grouping(g_v, 97, 251)))
                                {
                                    break lab4;
                                }
                                base.bra = base.cursor;
                                lab5: {
                                    var /** number */ v_4 = base.cursor;
                                    lab6: {
                                        if (!(base.eq_s("u")))
                                        {
                                            break lab6;
                                        }
                                        base.ket = base.cursor;
                                        if (!(base.in_grouping(g_v, 97, 251)))
                                        {
                                            break lab6;
                                        }
                                        if (!base.slice_from("U"))
                                        {
                                            return false;
                                        }
                                        break lab5;
                                    }
                                    base.cursor = v_4;
                                    lab7: {
                                        if (!(base.eq_s("i")))
                                        {
                                            break lab7;
                                        }
                                        base.ket = base.cursor;
                                        if (!(base.in_grouping(g_v, 97, 251)))
                                        {
                                            break lab7;
                                        }
                                        if (!base.slice_from("I"))
                                        {
                                            return false;
                                        }
                                        break lab5;
                                    }
                                    base.cursor = v_4;
                                    if (!(base.eq_s("y")))
                                    {
                                        break lab4;
                                    }
                                    base.ket = base.cursor;
                                    if (!base.slice_from("Y"))
                                    {
                                        return false;
                                    }
                                }
                                break lab3;
                            }
                            base.cursor = v_3;
                            lab8: {
                                base.bra = base.cursor;
                                if (!(base.eq_s("\u00EB")))
                                {
                                    break lab8;
                                }
                                base.ket = base.cursor;
                                if (!base.slice_from("He"))
                                {
                                    return false;
                                }
                                break lab3;
                            }
                            base.cursor = v_3;
                            lab9: {
                                base.bra = base.cursor;
                                if (!(base.eq_s("\u00EF")))
                                {
                                    break lab9;
                                }
                                base.ket = base.cursor;
                                if (!base.slice_from("Hi"))
                                {
                                    return false;
                                }
                                break lab3;
                            }
                            base.cursor = v_3;
                            lab10: {
                                base.bra = base.cursor;
                                if (!(base.eq_s("y")))
                                {
                                    break lab10;
                                }
                                base.ket = base.cursor;
                                if (!(base.in_grouping(g_v, 97, 251)))
                                {
                                    break lab10;
                                }
                                if (!base.slice_from("Y"))
                                {
                                    return false;
                                }
                                break lab3;
                            }
                            base.cursor = v_3;
                            if (!(base.eq_s("q")))
                            {
                                break lab2;
                            }
                            base.bra = base.cursor;
                            if (!(base.eq_s("u")))
                            {
                                break lab2;
                            }
                            base.ket = base.cursor;
                            if (!base.slice_from("U"))
                            {
                                return false;
                            }
                        }
                        base.cursor = v_2;
                        break golab1;
                    }
                    base.cursor = v_2;
                    if (base.cursor >= base.limit)
                    {
                        break lab0;
                    }
                    base.cursor++;
                }
                continue;
            }
            base.cursor = v_1;
            break;
        }
        return true;
    };

    /** @return {boolean} */
    function r_mark_regions() {
        I_pV = base.limit;
        I_p1 = base.limit;
        I_p2 = base.limit;
        var /** number */ v_1 = base.cursor;
        lab0: {
            lab1: {
                var /** number */ v_2 = base.cursor;
                lab2: {
                    if (!(base.in_grouping(g_v, 97, 251)))
                    {
                        break lab2;
                    }
                    if (!(base.in_grouping(g_v, 97, 251)))
                    {
                        break lab2;
                    }
                    if (base.cursor >= base.limit)
                    {
                        break lab2;
                    }
                    base.cursor++;
                    break lab1;
                }
                base.cursor = v_2;
                lab3: {
                    if (base.find_among(a_0) == 0)
                    {
                        break lab3;
                    }
                    break lab1;
                }
                base.cursor = v_2;
                if (base.cursor >= base.limit)
                {
                    break lab0;
                }
                base.cursor++;
                golab4: while(true)
                {
                    lab5: {
                        if (!(base.in_grouping(g_v, 97, 251)))
                        {
                            break lab5;
                        }
                        break golab4;
                    }
                    if (base.cursor >= base.limit)
                    {
                        break lab0;
                    }
                    base.cursor++;
                }
            }
            I_pV = base.cursor;
        }
        base.cursor = v_1;
        var /** number */ v_4 = base.cursor;
        lab6: {
            golab7: while(true)
            {
                lab8: {
                    if (!(base.in_grouping(g_v, 97, 251)))
                    {
                        break lab8;
                    }
                    break golab7;
                }
                if (base.cursor >= base.limit)
                {
                    break lab6;
                }
                base.cursor++;
            }
            golab9: while(true)
            {
                lab10: {
                    if (!(base.out_grouping(g_v, 97, 251)))
                    {
                        break lab10;
                    }
                    break golab9;
                }
                if (base.cursor >= base.limit)
                {
                    break lab6;
                }
                base.cursor++;
            }
            I_p1 = base.cursor;
            golab11: while(true)
            {
                lab12: {
                    if (!(base.in_grouping(g_v, 97, 251)))
                    {
                        break lab12;
                    }
                    break golab11;
                }
                if (base.cursor >= base.limit)
                {
                    break lab6;
                }
                base.cursor++;
            }
            golab13: while(true)
            {
                lab14: {
                    if (!(base.out_grouping(g_v, 97, 251)))
                    {
                        break lab14;
                    }
                    break golab13;
                }
                if (base.cursor >= base.limit)
                {
                    break lab6;
                }
                base.cursor++;
            }
            I_p2 = base.cursor;
        }
        base.cursor = v_4;
        return true;
    };

    /** @return {boolean} */
    function r_postlude() {
        var /** number */ among_var;
        while(true)
        {
            var /** number */ v_1 = base.cursor;
            lab0: {
                base.bra = base.cursor;
                among_var = base.find_among(a_1);
                if (among_var == 0)
                {
                    break lab0;
                }
                base.ket = base.cursor;
                switch (among_var) {
                    case 1:
                        if (!base.slice_from("i"))
                        {
                            return false;
                        }
                        break;
                    case 2:
                        if (!base.slice_from("u"))
                        {
                            return false;
                        }
                        break;
                    case 3:
                        if (!base.slice_from("y"))
                        {
                            return false;
                        }
                        break;
                    case 4:
                        if (!base.slice_from("\u00EB"))
                        {
                            return false;
                        }
                        break;
                    case 5:
                        if (!base.slice_from("\u00EF"))
                        {
                            return false;
                        }
                        break;
                    case 6:
                        if (!base.slice_del())
                        {
                            return false;
                        }
                        break;
                    case 7:
                        if (base.cursor >= base.limit)
                        {
                            break lab0;
                        }
                        base.cursor++;
                        break;
                }
                continue;
            }
            base.cursor = v_1;
            break;
        }
        return true;
    };

    /** @return {boolean} */
    function r_RV() {
        if (!(I_pV <= base.cursor))
        {
            return false;
        }
        return true;
    };

    /** @return {boolean} */
    function r_R1() {
        if (!(I_p1 <= base.cursor))
        {
            return false;
        }
        return true;
    };

    /** @return {boolean} */
    function r_R2() {
        if (!(I_p2 <= base.cursor))
        {
            return false;
        }
        return true;
    };

    /** @return {boolean} */
    function r_standard_suffix() {
        var /** number */ among_var;
        base.ket = base.cursor;
        among_var = base.find_among_b(a_4);
        if (among_var == 0)
        {
            return false;
        }
        base.bra = base.cursor;
        switch (among_var) {
            case 1:
                if (!r_R2())
                {
                    return false;
                }
                if (!base.slice_del())
                {
                    return false;
                }
                break;
            case 2:
                if (!r_R2())
                {
                    return false;
                }
                if (!base.slice_del())
                {
                    return false;
                }
                var /** number */ v_1 = base.limit - base.cursor;
                lab0: {
                    base.ket = base.cursor;
                    if (!(base.eq_s_b("ic")))
                    {
                        base.cursor = base.limit - v_1;
                        break lab0;
                    }
                    base.bra = base.cursor;
                    lab1: {
                        var /** number */ v_2 = base.limit - base.cursor;
                        lab2: {
                            if (!r_R2())
                            {
                                break lab2;
                            }
                            if (!base.slice_del())
                            {
                                return false;
                            }
                            break lab1;
                        }
                        base.cursor = base.limit - v_2;
                        if (!base.slice_from("iqU"))
                        {
                            return false;
                        }
                    }
                }
                break;
            case 3:
                if (!r_R2())
                {
                    return false;
                }
                if (!base.slice_from("log"))
                {
                    return false;
                }
                break;
            case 4:
                if (!r_R2())
                {
                    return false;
                }
                if (!base.slice_from("u"))
                {
                    return false;
                }
                break;
            case 5:
                if (!r_R2())
                {
                    return false;
                }
                if (!base.slice_from("ent"))
                {
                    return false;
                }
                break;
            case 6:
                if (!r_RV())
                {
                    return false;
                }
                if (!base.slice_del())
                {
                    return false;
                }
                var /** number */ v_3 = base.limit - base.cursor;
                lab3: {
                    base.ket = base.cursor;
                    among_var = base.find_among_b(a_2);
                    if (among_var == 0)
                    {
                        base.cursor = base.limit - v_3;
                        break lab3;
                    }
                    base.bra = base.cursor;
                    switch (among_var) {
                        case 1:
                            if (!r_R2())
                            {
                                base.cursor = base.limit - v_3;
                                break lab3;
                            }
                            if (!base.slice_del())
                            {
                                return false;
                            }
                            base.ket = base.cursor;
                            if (!(base.eq_s_b("at")))
                            {
                                base.cursor = base.limit - v_3;
                                break lab3;
                            }
                            base.bra = base.cursor;
                            if (!r_R2())
                            {
                                base.cursor = base.limit - v_3;
                                break lab3;
                            }
                            if (!base.slice_del())
                            {
                                return false;
                            }
                            break;
                        case 2:
                            lab4: {
                                var /** number */ v_4 = base.limit - base.cursor;
                                lab5: {
                                    if (!r_R2())
                                    {
                                        break lab5;
                                    }
                                    if (!base.slice_del())
                                    {
                                        return false;
                                    }
                                    break lab4;
                                }
                                base.cursor = base.limit - v_4;
                                if (!r_R1())
                                {
                                    base.cursor = base.limit - v_3;
                                    break lab3;
                                }
                                if (!base.slice_from("eux"))
                                {
                                    return false;
                                }
                            }
                            break;
                        case 3:
                            if (!r_R2())
                            {
                                base.cursor = base.limit - v_3;
                                break lab3;
                            }
                            if (!base.slice_del())
                            {
                                return false;
                            }
                            break;
                        case 4:
                            if (!r_RV())
                            {
                                base.cursor = base.limit - v_3;
                                break lab3;
                            }
                            if (!base.slice_from("i"))
                            {
                                return false;
                            }
                            break;
                    }
                }
                break;
            case 7:
                if (!r_R2())
                {
                    return false;
                }
                if (!base.slice_del())
                {
                    return false;
                }
                var /** number */ v_5 = base.limit - base.cursor;
                lab6: {
                    base.ket = base.cursor;
                    among_var = base.find_among_b(a_3);
                    if (among_var == 0)
                    {
                        base.cursor = base.limit - v_5;
                        break lab6;
                    }
                    base.bra = base.cursor;
                    switch (among_var) {
                        case 1:
                            lab7: {
                                var /** number */ v_6 = base.limit - base.cursor;
                                lab8: {
                                    if (!r_R2())
                                    {
                                        break lab8;
                                    }
                                    if (!base.slice_del())
                                    {
                                        return false;
                                    }
                                    break lab7;
                                }
                                base.cursor = base.limit - v_6;
                                if (!base.slice_from("abl"))
                                {
                                    return false;
                                }
                            }
                            break;
                        case 2:
                            lab9: {
                                var /** number */ v_7 = base.limit - base.cursor;
                                lab10: {
                                    if (!r_R2())
                                    {
                                        break lab10;
                                    }
                                    if (!base.slice_del())
                                    {
                                        return false;
                                    }
                                    break lab9;
                                }
                                base.cursor = base.limit - v_7;
                                if (!base.slice_from("iqU"))
                                {
                                    return false;
                                }
                            }
                            break;
                        case 3:
                            if (!r_R2())
                            {
                                base.cursor = base.limit - v_5;
                                break lab6;
                            }
                            if (!base.slice_del())
                            {
                                return false;
                            }
                            break;
                    }
                }
                break;
            case 8:
                if (!r_R2())
                {
                    return false;
                }
                if (!base.slice_del())
                {
                    return false;
                }
                var /** number */ v_8 = base.limit - base.cursor;
                lab11: {
                    base.ket = base.cursor;
                    if (!(base.eq_s_b("at")))
                    {
                        base.cursor = base.limit - v_8;
                        break lab11;
                    }
                    base.bra = base.cursor;
                    if (!r_R2())
                    {
                        base.cursor = base.limit - v_8;
                        break lab11;
                    }
                    if (!base.slice_del())
                    {
                        return false;
                    }
                    base.ket = base.cursor;
                    if (!(base.eq_s_b("ic")))
                    {
                        base.cursor = base.limit - v_8;
                        break lab11;
                    }
                    base.bra = base.cursor;
                    lab12: {
                        var /** number */ v_9 = base.limit - base.cursor;
                        lab13: {
                            if (!r_R2())
                            {
                                break lab13;
                            }
                            if (!base.slice_del())
                            {
                                return false;
                            }
                            break lab12;
                        }
                        base.cursor = base.limit - v_9;
                        if (!base.slice_from("iqU"))
                        {
                            return false;
                        }
                    }
                }
                break;
            case 9:
                if (!base.slice_from("eau"))
                {
                    return false;
                }
                break;
            case 10:
                if (!r_R1())
                {
                    return false;
                }
                if (!base.slice_from("al"))
                {
                    return false;
                }
                break;
            case 11:
                lab14: {
                    var /** number */ v_10 = base.limit - base.cursor;
                    lab15: {
                        if (!r_R2())
                        {
                            break lab15;
                        }
                        if (!base.slice_del())
                        {
                            return false;
                        }
                        break lab14;
                    }
                    base.cursor = base.limit - v_10;
                    if (!r_R1())
                    {
                        return false;
                    }
                    if (!base.slice_from("eux"))
                    {
                        return false;
                    }
                }
                break;
            case 12:
                if (!r_R1())
                {
                    return false;
                }
                if (!(base.out_grouping_b(g_v, 97, 251)))
                {
                    return false;
                }
                if (!base.slice_del())
                {
                    return false;
                }
                break;
            case 13:
                if (!r_RV())
                {
                    return false;
                }
                if (!base.slice_from("ant"))
                {
                    return false;
                }
                return false;
            case 14:
                if (!r_RV())
                {
                    return false;
                }
                if (!base.slice_from("ent"))
                {
                    return false;
                }
                return false;
            case 15:
                var /** number */ v_11 = base.limit - base.cursor;
                if (!(base.in_grouping_b(g_v, 97, 251)))
                {
                    return false;
                }
                if (!r_RV())
                {
                    return false;
                }
                base.cursor = base.limit - v_11;
                if (!base.slice_del())
                {
                    return false;
                }
                return false;
        }
        return true;
    };

    /** @return {boolean} */
    function r_i_verb_suffix() {
        if (base.cursor < I_pV)
        {
            return false;
        }
        var /** number */ v_2 = base.limit_backward;
        base.limit_backward = I_pV;
        base.ket = base.cursor;
        if (base.find_among_b(a_5) == 0)
        {
            base.limit_backward = v_2;
            return false;
        }
        base.bra = base.cursor;
        {
            var /** number */ v_3 = base.limit - base.cursor;
            lab0: {
                if (!(base.eq_s_b("H")))
                {
                    break lab0;
                }
                base.limit_backward = v_2;
                return false;
            }
            base.cursor = base.limit - v_3;
        }
        if (!(base.out_grouping_b(g_v, 97, 251)))
        {
            base.limit_backward = v_2;
            return false;
        }
        if (!base.slice_del())
        {
            return false;
        }
        base.limit_backward = v_2;
        return true;
    };

    /** @return {boolean} */
    function r_verb_suffix() {
        var /** number */ among_var;
        if (base.cursor < I_pV)
        {
            return false;
        }
        var /** number */ v_2 = base.limit_backward;
        base.limit_backward = I_pV;
        base.ket = base.cursor;
        among_var = base.find_among_b(a_6);
        if (among_var == 0)
        {
            base.limit_backward = v_2;
            return false;
        }
        base.bra = base.cursor;
        switch (among_var) {
            case 1:
                if (!r_R2())
                {
                    base.limit_backward = v_2;
                    return false;
                }
                if (!base.slice_del())
                {
                    return false;
                }
                break;
            case 2:
                if (!base.slice_del())
                {
                    return false;
                }
                break;
            case 3:
                if (!base.slice_del())
                {
                    return false;
                }
                var /** number */ v_3 = base.limit - base.cursor;
                lab0: {
                    base.ket = base.cursor;
                    if (!(base.eq_s_b("e")))
                    {
                        base.cursor = base.limit - v_3;
                        break lab0;
                    }
                    base.bra = base.cursor;
                    if (!base.slice_del())
                    {
                        return false;
                    }
                }
                break;
        }
        base.limit_backward = v_2;
        return true;
    };

    /** @return {boolean} */
    function r_residual_suffix() {
        var /** number */ among_var;
        var /** number */ v_1 = base.limit - base.cursor;
        lab0: {
            base.ket = base.cursor;
            if (!(base.eq_s_b("s")))
            {
                base.cursor = base.limit - v_1;
                break lab0;
            }
            base.bra = base.cursor;
            var /** number */ v_2 = base.limit - base.cursor;
            lab1: {
                var /** number */ v_3 = base.limit - base.cursor;
                lab2: {
                    if (!(base.eq_s_b("Hi")))
                    {
                        break lab2;
                    }
                    break lab1;
                }
                base.cursor = base.limit - v_3;
                if (!(base.out_grouping_b(g_keep_with_s, 97, 232)))
                {
                    base.cursor = base.limit - v_1;
                    break lab0;
                }
            }
            base.cursor = base.limit - v_2;
            if (!base.slice_del())
            {
                return false;
            }
        }
        if (base.cursor < I_pV)
        {
            return false;
        }
        var /** number */ v_5 = base.limit_backward;
        base.limit_backward = I_pV;
        base.ket = base.cursor;
        among_var = base.find_among_b(a_7);
        if (among_var == 0)
        {
            base.limit_backward = v_5;
            return false;
        }
        base.bra = base.cursor;
        switch (among_var) {
            case 1:
                if (!r_R2())
                {
                    base.limit_backward = v_5;
                    return false;
                }
                lab3: {
                    var /** number */ v_6 = base.limit - base.cursor;
                    lab4: {
                        if (!(base.eq_s_b("s")))
                        {
                            break lab4;
                        }
                        break lab3;
                    }
                    base.cursor = base.limit - v_6;
                    if (!(base.eq_s_b("t")))
                    {
                        base.limit_backward = v_5;
                        return false;
                    }
                }
                if (!base.slice_del())
                {
                    return false;
                }
                break;
            case 2:
                if (!base.slice_from("i"))
                {
                    return false;
                }
                break;
            case 3:
                if (!base.slice_del())
                {
                    return false;
                }
                break;
        }
        base.limit_backward = v_5;
        return true;
    };

    /** @return {boolean} */
    function r_un_double() {
        var /** number */ v_1 = base.limit - base.cursor;
        if (base.find_among_b(a_8) == 0)
        {
            return false;
        }
        base.cursor = base.limit - v_1;
        base.ket = base.cursor;
        if (base.cursor <= base.limit_backward)
        {
            return false;
        }
        base.cursor--;
        base.bra = base.cursor;
        if (!base.slice_del())
        {
            return false;
        }
        return true;
    };

    /** @return {boolean} */
    function r_un_accent() {
        {
            var v_1 = 1;
            while(true)
            {
                lab0: {
                    if (!(base.out_grouping_b(g_v, 97, 251)))
                    {
                        break lab0;
                    }
                    v_1--;
                    continue;
                }
                break;
            }
            if (v_1 > 0)
            {
                return false;
            }
        }
        base.ket = base.cursor;
        lab1: {
            var /** number */ v_3 = base.limit - base.cursor;
            lab2: {
                if (!(base.eq_s_b("\u00E9")))
                {
                    break lab2;
                }
                break lab1;
            }
            base.cursor = base.limit - v_3;
            if (!(base.eq_s_b("\u00E8")))
            {
                return false;
            }
        }
        base.bra = base.cursor;
        if (!base.slice_from("e"))
        {
            return false;
        }
        return true;
    };

    this.stem = /** @return {boolean} */ function() {
        var /** number */ v_1 = base.cursor;
        r_prelude();
        base.cursor = v_1;
        r_mark_regions();
        base.limit_backward = base.cursor; base.cursor = base.limit;
        var /** number */ v_3 = base.limit - base.cursor;
        lab0: {
            lab1: {
                var /** number */ v_4 = base.limit - base.cursor;
                lab2: {
                    var /** number */ v_5 = base.limit - base.cursor;
                    lab3: {
                        var /** number */ v_6 = base.limit - base.cursor;
                        lab4: {
                            if (!r_standard_suffix())
                            {
                                break lab4;
                            }
                            break lab3;
                        }
                        base.cursor = base.limit - v_6;
                        lab5: {
                            if (!r_i_verb_suffix())
                            {
                                break lab5;
                            }
                            break lab3;
                        }
                        base.cursor = base.limit - v_6;
                        if (!r_verb_suffix())
                        {
                            break lab2;
                        }
                    }
                    base.cursor = base.limit - v_5;
                    var /** number */ v_7 = base.limit - base.cursor;
                    lab6: {
                        base.ket = base.cursor;
                        lab7: {
                            var /** number */ v_8 = base.limit - base.cursor;
                            lab8: {
                                if (!(base.eq_s_b("Y")))
                                {
                                    break lab8;
                                }
                                base.bra = base.cursor;
                                if (!base.slice_from("i"))
                                {
                                    return false;
                                }
                                break lab7;
                            }
                            base.cursor = base.limit - v_8;
                            if (!(base.eq_s_b("\u00E7")))
                            {
                                base.cursor = base.limit - v_7;
                                break lab6;
                            }
                            base.bra = base.cursor;
                            if (!base.slice_from("c"))
                            {
                                return false;
                            }
                        }
                    }
                    break lab1;
                }
                base.cursor = base.limit - v_4;
                if (!r_residual_suffix())
                {
                    break lab0;
                }
            }
        }
        base.cursor = base.limit - v_3;
        var /** number */ v_9 = base.limit - base.cursor;
        r_un_double();
        base.cursor = base.limit - v_9;
        var /** number */ v_10 = base.limit - base.cursor;
        r_un_accent();
        base.cursor = base.limit - v_10;
        base.cursor = base.limit_backward;
        var /** number */ v_11 = base.cursor;
        r_postlude();
        base.cursor = v_11;
        return true;
    };

    /**@return{string}*/
    this['stemWord'] = function(/**string*/word) {
        base.setCurrent(word);
        this.stem();
        return base.getCurrent();
    };
};

Stemmer = FrenchStemmer;
