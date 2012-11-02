#ifndef MANTID_API_ALGORITHMFACTORY_H_
#define MANTID_API_ALGORITHMFACTORY_H_

//----------------------------------------------------------------------
// Includes
//----------------------------------------------------------------------
#include <vector>
#include <set>
#include "MantidAPI/DllConfig.h"
#include "MantidKernel/DynamicFactory.h"
#include "MantidKernel/SingletonHolder.h"
#include "MantidKernel/Logger.h"

namespace Mantid
{
namespace API
{

/// Structure uniquely describing an algorithm with its name, category and version.
struct Algorithm_descriptor
{
  std::string name;///< name
  std::string category;///< category
  int version;///< version
};

//----------------------------------------------------------------------
// Forward declarations
//----------------------------------------------------------------------
class IAlgorithm;
class Algorithm;

/** The AlgorithmFactory class is in charge of the creation of concrete
    instances of Algorithms. It inherits most of its implementation from
    the Dynamic Factory base class.
    It is implemented as a singleton class.
    
    @author Russell Taylor, Tessella Support Services plc
    @date 21/09/2007
    
    Copyright &copy; 2007-2011 ISIS Rutherford Appleton Laboratory & NScD Oak Ridge National Laboratory

    This file is part of Mantid.

    Mantid is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    Mantid is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    File change history is stored at: <https://github.com/mantidproject/mantid>    
*/
class MANTID_API_DLL AlgorithmFactoryImpl : public Kernel::DynamicFactory<Algorithm>
{
public:
  // Unhide the base class version (to satisfy the intel compiler)
  using Kernel::DynamicFactory<Algorithm>::create;
  ///Creates an instance of an algorithm
  boost::shared_ptr<Algorithm> create(const std::string& ,const int& ) const;

  /// algorithm factory specific function to subscribe algorithms, calls the dynamic factory subscribe function internally
  template <class C>
  void subscribe()
  {
    Kernel::Instantiator<C, Algorithm>* newI = new Kernel::Instantiator<C, Algorithm>;
    this->subscribe(newI);
  }

  /**
   * Subscribes an algorithm using a custom instantiator. This
   * object takes ownership of the instantiator
   * @param instantiator - A pointer to a custom instantiator
   * @param replaceExisting - If true an existing algorithm of the same name and version is replaced
   */
  template<class T>
  void subscribe(Kernel::AbstractInstantiator<T> *instantiator, const bool replaceExisting = false)
  {
    boost::shared_ptr<IAlgorithm> tempAlg = instantiator-> createInstance();
    const int version = extractAlgVersion(tempAlg);
    const std::string className = extractAlgName(tempAlg);
    typename VersionMap::const_iterator it = m_vmap.find(className);
    if (!className.empty())
    {
      const std::string key = createName(className,version);
      if( it == m_vmap.end() )
      {
        m_vmap[className] = version;
      }
      else
      {
        if( replaceExisting )
        {
          Kernel::DynamicFactory<Algorithm>::unsubscribe(key);
        }
        else if(version == it->second)
        {
          g_log.fatal() << "Cannot register algorithm " << className << " twice with the same version\n";
          return;
        }
        if(version > it->second)
        {
          m_vmap[className]=version;
        }
      }  
      Kernel::DynamicFactory<Algorithm>::subscribe(key, instantiator);
    }
  }
  /// Unsubscribe the given algorithm
  void unsubscribe(const std::string & algorithmName, const int version);
  /// Does an algorithm of the given name and version exist
  bool exists(const std::string & algorithmName, const int version = -1);

  /// Get the algorithm names and version - mangled use decodeName to separate
  const std::vector<std::string> getKeys() const;
  const std::vector<std::string> getKeys(bool includeHidden) const;
  
  ///Get the algorithm categories
  const std::set<std::string> getCategories(bool includeHidden=false) const;

  ///Get the algorithm categories
  const std::map<std::string,bool> getCategoriesWithState() const;

  /// Returns algorithm descriptors.
  std::vector<Algorithm_descriptor> getDescriptors(bool includeHidden=false) const;

  ///unmangles the names used as keys into the name and version
  std::pair<std::string,int> decodeName(const std::string& mangledName)const;

 private:
  friend struct Mantid::Kernel::CreateUsingNew<AlgorithmFactoryImpl>;

  /// Extract the name of an algorithm
  const std::string extractAlgName(const boost::shared_ptr<IAlgorithm> alg) const;
  /// Extract the version of an algorithm
  int extractAlgVersion(const boost::shared_ptr<IAlgorithm> alg) const;

  ///Create an algorithm object with the specified name
  boost::shared_ptr<Algorithm> createAlgorithm(const std::string & name, const int version) const;
        
  /// Private Constructor for singleton class
  AlgorithmFactoryImpl();       
  /// Private copy constructor - NO COPY ALLOWED
  AlgorithmFactoryImpl(const AlgorithmFactoryImpl&);
  /// Private assignment operator - NO ASSIGNMENT ALLOWED
  AlgorithmFactoryImpl& operator = (const AlgorithmFactoryImpl&);
  ///Private Destructor
  virtual ~AlgorithmFactoryImpl();
  /// creates an algorithm name convolved from an name and version
  std::string createName(const std::string&, const int&)const;
  /// fills a set with the hidden categories
  void fillHiddenCategories(std::set<std::string> *categorySet) const;
  ///static reference to the logger class
  Kernel::Logger& g_log;

  /// A typedef for the map of algorithm versions
  typedef std::map<std::string, int> VersionMap;
  /// The map holding the registered class names and their highest versions
  VersionMap m_vmap;
};
  

///Forward declaration of a specialisation of SingletonHolder for AlgorithmFactoryImpl (needed for dllexport/dllimport) and a typedef for it.
#ifdef _WIN32
// this breaks new namespace declaraion rules; need to find a better fix
template class MANTID_API_DLL Mantid::Kernel::SingletonHolder<AlgorithmFactoryImpl>;
#endif /* _WIN32 */

typedef MANTID_API_DLL Mantid::Kernel::SingletonHolder<AlgorithmFactoryImpl> AlgorithmFactory;

/// Convenient typedef for an UpdateNotification
typedef Mantid::Kernel::DynamicFactory<Algorithm>::UpdateNotification AlgorithmFactoryUpdateNotification;
typedef const Poco::AutoPtr<Mantid::Kernel::DynamicFactory<Algorithm>::UpdateNotification> & AlgorithmFactoryUpdateNotification_ptr;

} // namespace API
} // namespace Mantid

#endif /*MANTID_API_ALGORITHMFACTORY_H_*/
