#ifndef ASPARSERATIONS_GRAMMAR_GRAMMAR_H_
#define ASPARSERATIONS_GRAMMAR_GRAMMAR_H_

#include "nonterminal.hpp"
#include "token.hpp"
#include <list>
#include <map>
#include <set>
#include <string>
#include <vector>

namespace asparserations {
  namespace grammar {
    class Grammar
    {
    public:
      //Constructor
      Grammar(const std::string&);
      //Move constructor
      Grammar(Grammar&&);

      /**
         Adds a token to the grammar
         @param id the name of the token
         @return a reference to the newly added token
       */
      Token& add_token(const std::string&);

      /**
         Adds a nonterminal to the grammar
         @param id the name of the nonterminal
         @return a reference to the newly added nonterminal
       */
      Nonterminal& add_nonterminal(const std::string&);

      /**
         Gets token by id
         @param the key of the token
         @return a reference to the corresponding token
       */
      Token& token_at(const std::string&);
      const Token& token_at(const std::string&) const;

      /**
         Gets nonterminal by id
         @param the key of the nonterminal
         @return a reference to the nonterminal
       */
      Nonterminal& nonterminal_at(const std::string&);
      const Nonterminal& nonterminal_at(const std::string&) const;

      const std::vector<const Nonterminal*>& nonterminals() const;
      const std::vector<const Token*>& tokens() const;
      const Nonterminal& accept() const;
      const Token& end() const;

      /**
         Returns the start symbol
       */
      Nonterminal& start_symbol();
      const Nonterminal& start_symbol() const;

      /**
         Sets the start symbol
       */
      void set_start_symbol(Nonterminal&);

      /**
         Computes the FIRST sets of the symbols - the set of tokens that the
         symbol can start with

         Only call after grammar has been completely constructed!
       */
      void compute_first_sets();
    private:
      Grammar(const Grammar&) = delete;

      struct TokenImp : public Token
      {
        // Methods
        TokenImp(Grammar& g, const std::string& id, unsigned int);
        const std::string& name() const;
	unsigned int index() const;
        Grammar& grammar();
        const Grammar& grammar() const;
        const std::set<std::reference_wrapper<const Token>>& first_set() const;
        const std::list<Production>& productions() const;
        bool is_token() const;
        bool derives_empty_string() const;
        // Members
        const std::string m_name;
        const unsigned int m_index;
        Grammar* m_grammar;
        std::set<std::reference_wrapper<const Token>> m_first_set;
        const std::list<Production> m_productions;
      };

      struct NonterminalImp : public Nonterminal
      {
        // Methods
        NonterminalImp(Grammar& g, const std::string& id, unsigned int);	
        const std::list<Production>& productions() const;
        Production& production_at(const std::string&);
        const Production& production_at(const std::string&) const;
        const std::string& name() const;
	unsigned int index() const;
        Grammar& grammar();
        const Grammar& grammar() const;
        const std::set<std::reference_wrapper<const Token>>& first_set() const;
        bool is_token() const;
        bool derives_empty_string() const;
        Production& add_production(const std::string&,
                                   std::vector<const Symbol*>);
	// Members
	const std::string m_name;
        const unsigned int m_index;
        Grammar* m_grammar;
        std::list<Production> m_productions;
	std::map<std::string,Production*> m_production_map;
        std::set<std::reference_wrapper<const Token>> m_first_set;
        bool m_derives_empty_string;
      };

      std::vector<const Token*> m_token_vec;
      std::vector<const Nonterminal*> m_nonterminal_vec;
      std::map<std::string,TokenImp> m_tokens;
      std::map<std::string,NonterminalImp> m_nonterminals;
      Nonterminal* m_start_symbol;
      TokenImp m_end;
      NonterminalImp m_accept;
    };
  }
}

#endif
