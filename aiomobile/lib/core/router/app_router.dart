import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/presentation/bloc/auth_bloc.dart';
import '../../features/auth/presentation/pages/login_page.dart';
import '../../features/home/presentation/pages/home_page.dart';

abstract class AppRoutes {
  static const login = '/login';
  static const home = '/';
}

GoRouter buildRouter(AuthBloc authBloc) => GoRouter(
      initialLocation: AppRoutes.home,
      refreshListenable: GoRouterAuthNotifier(authBloc),
      redirect: (BuildContext context, GoRouterState state) {
        final isAuth = authBloc.state is AuthAuthenticated;
        final isOnLogin = state.matchedLocation == AppRoutes.login;

        if (!isAuth && !isOnLogin) return AppRoutes.login;
        if (isAuth && isOnLogin) return AppRoutes.home;
        return null;
      },
      routes: [
        GoRoute(
          path: AppRoutes.home,
          builder: (context, state) => const HomePage(),
        ),
        GoRoute(
          path: AppRoutes.login,
          builder: (context, state) => const LoginPage(),
        ),
      ],
    );

// Bridges BLoC stream → GoRouter refresh (ChangeNotifier pattern).
final class GoRouterAuthNotifier extends ChangeNotifier {
  GoRouterAuthNotifier(AuthBloc bloc) {
    bloc.stream.listen((_) => notifyListeners());
  }
}
