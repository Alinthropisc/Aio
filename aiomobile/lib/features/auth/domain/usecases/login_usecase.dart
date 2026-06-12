import 'package:injectable/injectable.dart';
import '../entities/user.dart';
import '../repositories/auth_repository.dart';

final class LoginParams {
  final String email;
  final String password;
  const LoginParams({required this.email, required this.password});
}

@lazySingleton
class LoginUseCase {
  final AuthRepository _repository;
  const LoginUseCase(this._repository);

  AuthResult<({User user, String accessToken})> call(LoginParams params) =>
      _repository.login(email: params.email, password: params.password);
}
