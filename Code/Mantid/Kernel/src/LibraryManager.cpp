//----------------------------------------------------------------------
// Includes
//----------------------------------------------------------------------
#include <iostream>

#include "MantidKernel/DllOpen.h"
#include "MantidKernel/LibraryManager.h"

namespace Mantid
{
namespace Kernel
{
	/// Constructor
	LibraryManager::LibraryManager() : module(0)
	{}

	/// Destructor
	LibraryManager::~LibraryManager()
	{
		//Close lib
		if (module)
		{
			DllOpen::CloseDll(module);
			module = 0;
		}
	}

	/** Opens a DLL
	 *  @param libName The name of the file to open (not including the lib/so/dll)
	 *  @return True if DLL is opened or already open
	 */
	bool LibraryManager::OpenLibrary(const std::string& libName)
	{
		if (!module)
		{		
			//Load dynamically loaded library
			module = DllOpen::OpenDll(libName);
			if (!module) 
			{
				std::cout << "Could not open library!\n";
				return false;
			}
		}
	
		return true;
	}


} // namespace Kernel
} // namespace Mantid

