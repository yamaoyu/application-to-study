import { createStore } from 'vuex'
import { moduleTodo } from './modules/todo'
import { authenticateModule } from './modules/authenticate'

export default createStore({
  modules: {
    moduleTodo: moduleTodo,
    authenticateModule: authenticateModule
  }
})