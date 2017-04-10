#ifndef _ASPARSERATIONS_TABLE_ITEM_SET_H_
#define _ASPARSERATIONS_TABLE_ITEM_SET_H_

#include "item.hpp"
#include <set>

namespace asparserations {
  namespace table {
    class Item_Set
    {
      friend bool operator<(const Item_Set&, const Item_Set&);
    public:
      Item_Set(const std::set<Item>&);
      const std::set<Item>& items() const;
    private:
      std::set<Item> _items;
    };

    bool operator<(const Item_Set&, const Item_Set&);
  }
}

#endif
