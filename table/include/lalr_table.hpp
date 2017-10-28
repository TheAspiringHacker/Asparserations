#ifndef ASPARSERATIONS_TABLE_LALR_TABLE_H_
#define ASPARSERATIONS_TABLE_LALR_TABLE_H_

#include "item_core.hpp"
#include "lalr_state.hpp"
#include "state.hpp"
#include "table.hpp"
#include <list>

namespace asparserations {
  namespace grammar {
    class Grammar;
    class Production;
  }
  namespace table {
    class LALR_Table : public Table
    {
    public:
      LALR_Table(grammar::Grammar&);
      const std::list<State>& states() const;
      const grammar::Grammar& grammar() const;
    private:
      std::list<State> m_states;
      grammar::Grammar& m_grammar;
    };
  }
}

#endif
